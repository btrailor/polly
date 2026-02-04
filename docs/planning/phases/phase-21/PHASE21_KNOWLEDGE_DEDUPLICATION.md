# Phase 21: Knowledge Base Deduplication

**Status:** ✅ COMPLETE (January 28, 2026)  
**Priority:** High (Tier 1 - Core Intelligence)  
**Actual Effort:** 2-3 days  
**Complexity:** Medium

**Prerequisites:** 
- ✅ Phase 16 (Native Notes System) - COMPLETE
- ✅ Phase 2 (RAG System) - COMPLETE

---

## Executive Summary

Prevent duplicate notes in the knowledge base by detecting semantic similarity before note creation. When Polly finds similar existing notes, offer to append, link, or create new with automatic wikilinks to related content. This reduces knowledge fragmentation and encourages note consolidation over time.

## Current State (Updated Jan 28, 2026)

**What Exists:**
- ✅ **Native Polly notes system** (`/polly/notes/create` endpoint - server.py:1649)
- ✅ **NotesIndex** for tracking all notes with metadata (core/notes_index.py)
- ✅ **RAG system** with semantic search (core/rag.py:679)
- ✅ **Notes browser UI** with create/edit/manage (electron-app/src/renderer/notes-manager.js)
- ✅ **BacklinksIndex** for tracking note relationships (core/backlinks.py)

**The Problem:**
- ❌ No semantic similarity check before note creation
- ❌ No "similar notes found" warning
- ❌ No suggestion to link or append instead of duplicating
- ❌ Users can unknowingly create duplicate or highly similar notes
- ❌ Knowledge base becomes fragmented over time

**Integration Points (UPDATED):**
- `/interfaces/server.py:1649` - `/polly/notes/create` endpoint (native notes)
- `/core/notes_index.py` - NotesIndex for finding existing notes
- `/core/rag.py:679` - RAG search for semantic similarity
- `/electron-app/src/renderer/notes-manager.js` - Notes UI and creation flow
- `/electron-app/src/renderer/index.html` - Note creation modal

---

## User Experience

### Before This Feature

```
User: "Polly, create a note about infinite games framework"
Polly: Creates "Infinite Games Framework.md"

[2 weeks later]

User: "Polly, create a note about continuation over completion"
Polly: Creates "Continuation Over Completion.md"

Result: Two notes with 80% overlapping content
```

### After This Feature

```
User: "Polly, create a note about continuation over completion"

┌─────────────────────────────────────────────────────────┐
│ ⚠️  Similar Notes Found                                  │
├─────────────────────────────────────────────────────────┤
│ Polly found existing notes that might be related.       │
│ Consider appending or linking instead of creating new.  │
│                                                          │
│ ○ Infinite Games Framework.md              85% similar  │
│   "Playing to keep the game going rather than to win.   │
│   Focuses on continuation over completion..."           │
│   ~/vault/Grids/Mental-Models/                          │
│                                                          │
│ ○ Game Theory Notes.md                     72% similar  │
│   "Finite vs infinite games, competitive vs..."         │
│   ~/vault/Grids/Concepts/                               │
│                                                          │
│ [ Append to Selected Note ]                             │
│ [ Create with Links ]                                   │
│ [ Create New Note Anyway ]                              │
└─────────────────────────────────────────────────────────┘

User selects: "Append to Selected Note"
Polly: Appends to "Infinite Games Framework.md" with separator

Result: Single comprehensive note, no duplication
```

---

## Technical Implementation (UPDATED for Native Notes)

### Architecture Changes

**OLD Architecture (Obsidian-based):**
- Dedup engine in `/integrations/obsidian_dedup.py`
- Coupled to Obsidian integration
- Modified `obsidian.create_note()` method

**NEW Architecture (Native Notes):**
- Dedup engine in `/core/notes_dedup.py` (core system, not integration)
- Works with `NotesIndex` and RAG
- Integrates with `/polly/notes/create` endpoint
- No dependency on Obsidian integration

### Day 1: Similarity Detection Engine (6-8 hours)

#### Morning: Core Deduplication Logic

Create `/core/notes_dedup.py`:

```python
"""
Knowledge Base Deduplication System
Prevents duplicate notes by detecting semantic similarity before creation.
Works with native Polly notes system.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class SimilarNote:
    """A note that's similar to proposed content."""
    path: str          # Full file path
    name: str          # Note filename without extension
    title: str         # Display title
    domain: str        # Folder/domain name
    similarity: float  # 0.0 - 1.0
    snippet: str       # Most relevant excerpt (200 chars)
    
    def to_dict(self):
        """Convert to dict for JSON serialization."""
        return asdict(self)
    
class DeduplicationEngine:
    """Detects duplicate/similar content in knowledge base using RAG."""
    
    def __init__(self, rag_system, notes_index):
        """
        Initialize deduplication engine.
        
        Args:
            rag_system: UnifiedRAG instance for semantic search
            notes_index: NotesIndex instance for note metadata
        """
        self.rag = rag_system
        self.notes_index = notes_index
        
    def check_similarity(
        self,
        content: str,
        title: str,
        similarity_threshold: float = 0.70,
        max_results: int = 5
    ) -> List[SimilarNote]:
        """
        Check if proposed note is similar to existing notes.
        
        Args:
            content: Proposed note content
            title: Proposed note title
            similarity_threshold: Min similarity to flag (0.70 = 70%)
            max_results: Maximum number of similar notes to return
        
        Returns:
            List of similar notes with scores, sorted by similarity
        """
        # Search using RAG with generous n_results
        # Note: RAG.search() is synchronous, not async
        results = self.rag.search(
            query=f"{title}\n\n{content}",
            n_results=10,
            source_types=['notes']  # Only search notes collection
        )
        
        similar_notes = []
        
        for result in results:
            # result is a SearchResult object with score and doc
            score = result.score
            doc = result.doc
            
            # Check if similarity exceeds threshold
            if score >= similarity_threshold:
                # Get note metadata from NotesIndex
                note_path = Path(doc.metadata.get('filepath', ''))
                note_info = self.notes_index.find_note_by_path(note_path)
                
                if note_info:
                    # Extract relevant snippet from the matched content
                    snippet = self._extract_snippet(
                        doc.content,
                        max_length=200
                    )
                    
                    similar_notes.append(SimilarNote(
                        path=str(note_info.path),
                        name=note_info.name,
                        title=note_info.title or note_info.name,
                        domain=note_info.domain or 'Unknown',
                        similarity=score,
                        snippet=snippet
                    ))
        
        # Sort by similarity (highest first) and limit results
        similar_notes.sort(key=lambda x: x.similarity, reverse=True)
        similar_notes = similar_notes[:max_results]
        
        logger.info(f"Found {len(similar_notes)} similar notes for '{title}' (threshold: {similarity_threshold})")
        return similar_notes
    
    def _extract_snippet(self, content: str, max_length: int = 200) -> str:
        """
        Extract most relevant snippet from content.
        
        Args:
            content: Full content text
            max_length: Maximum snippet length
            
        Returns:
            Snippet string with ellipsis if truncated
        """
        # Strip frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Strip markdown headers
        lines = content.split('\n')
        cleaned_lines = [l for l in lines if not l.strip().startswith('#')]
        cleaned_content = '\n'.join(cleaned_lines).strip()
        
        if len(cleaned_content) <= max_length:
            return cleaned_content
        
        # Truncate at word boundary
        truncated = cleaned_content[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # Only if we're close to the limit
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def suggest_links(
        self,
        similar_notes: List[SimilarNote]
    ) -> List[str]:
        """
        Suggest wikilinks to add to the new note.
        
        Args:
            similar_notes: List of similar notes
        
        Returns:
            List of wikilink strings: ["[[Note Name]]", ...]
        """
        links = []
        
        # Top 5 most similar notes become wikilinks
        for note in similar_notes[:5]:
            # Use the note name for wikilink (without extension)
            links.append(f"[[{note.name}]]")
        
        return links


# Global singleton instance
_dedup_engine = None

def get_dedup_engine():
    """Get the global deduplication engine instance."""
    return _dedup_engine

def init_dedup_engine(rag_system, notes_index):
    """Initialize the global deduplication engine."""
    global _dedup_engine
    _dedup_engine = DeduplicationEngine(rag_system, notes_index)
    logger.info("Deduplication engine initialized")
    return _dedup_engine
```

#### Afternoon: Integration with `/polly/notes/create` Endpoint

Update `/interfaces/server.py` (around line 1649):

```python

@app.post("/polly/notes/create")
async def create_note(request: Dict[str, Any]):
    """
    Create a new note with duplicate detection.
    
    Request: {
        "name": "Note Name",
        "domain": "02-Signals",
        "content": "# Note Name\\n\\nInitial content...",
        "check_duplicates": true  # NEW: Enable duplicate detection (default: true)
    }
    
    Response (if duplicates found): {
        "status": "similar_found",
        "similar_notes": [
            {
                "path": "/full/path/to/note.md",
                "name": "note_name",
                "title": "Note Title",
                "domain": "02-Signals",
                "similarity": 0.85,
                "snippet": "First 200 chars of content..."
            }
        ],
        "proposed_note": {
            "name": "proposed_note_name",
            "domain": "02-Signals",
            "content": "..."
        }
    }
    
    Response (if no duplicates or check_duplicates=false): {
        "success": true,
        "note": { ... }  # Standard creation response
    }
    """
    try:
        from core.notes_dedup import get_dedup_engine
        from core.notes_index import get_notes_index
        from core.notes_source_manager import NotesSourceManager
        
        # Get parameters
        name = request.get("name")
        domain = request.get("domain")
        content = request.get("content", "")
        check_duplicates = request.get("check_duplicates", True)
        
        if not name or not domain:
            raise HTTPException(400, "Note name and domain are required")
        
        # Normalize filename
        filename = name.lower().replace(" ", "_").replace("-", "_")
        filename = re.sub(r'[^\w_]', '', filename)
        
        # Get notes path
        manager = NotesSourceManager()
        notes_path = Path(manager.get_notes_path()).expanduser()
        domain_path = notes_path / domain
        note_path = domain_path / f"{filename}.md"
        
        # Check if note already exists
        if note_path.exists():
            raise HTTPException(409, f"Note '{filename}' already exists in {domain}")
        
        # Check for similar notes if enabled
        if check_duplicates:
            dedup_engine = get_dedup_engine()
            if dedup_engine:
                try:
                    similar_notes = dedup_engine.check_similarity(
                        content=content,
                        title=name,
                        similarity_threshold=0.70,  # 70% threshold
                        max_results=5
                    )
                    
                    if similar_notes:
                        # Return similar notes for user decision
                        return {
                            "status": "similar_found",
                            "similar_notes": [n.to_dict() for n in similar_notes],
                            "proposed_note": {
                                "name": filename,
                                "title": name,
                                "domain": domain,
                                "content": content
                            }
                        }
                except Exception as e:
                    logger.error(f"Duplicate check failed: {e}")
                    # Continue with creation - dedup is nice-to-have
        
        # No duplicates found or check disabled - proceed with creation
        # Create domain folder if needed
        if not domain_path.exists():
            domain_path.mkdir(parents=True, exist_ok=True)
        
        # Create basic content if none provided
        if not content:
            content = f"# {name}\n\n"
        
        # Write note file
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created note: {note_path}")
        
        # Re-index to include new note
        notes_idx = get_notes_index()
        notes_idx.build_index(notes_path, recursive=True)
        
        # Get the newly created note's info
        created_note = notes_idx.find_note_by_name(filename)
        
        return {
            "success": True,
            "note": {
                "path": str(created_note.path) if created_note else str(note_path),
                "name": created_note.name if created_note else filename,
                "title": created_note.title if created_note else name,
                "domain": created_note.domain if created_note else domain
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create note failed: {e}")
        raise HTTPException(500, f"Failed to create note: {str(e)}")


# NEW ENDPOINT: Append to existing note
@app.post("/polly/notes/append")
async def append_to_note(request: Dict[str, Any]):
    """
    Append content to an existing note.
    
    Request: {
        "path": "/full/path/to/note.md",
        "content": "Content to append...",
        "separator": "\\n\\n---\\n\\n"  # Optional separator
    }
    
    Response: {
        "success": true,
        "note_path": "relative/path/to/note.md"
    }
    """
    try:
        note_path = Path(request.get("path"))
        content = request.get("content", "")
        separator = request.get("separator", "\n\n---\n\n")
        
        if not note_path.exists():
            raise HTTPException(404, f"Note not found: {note_path}")
        
        # Read existing content
        existing = note_path.read_text(encoding='utf-8')
        
        # Append with separator
        new_content = existing + separator + content
        
        # Write back
        note_path.write_text(new_content, encoding='utf-8')
        
        logger.info(f"Appended to note: {note_path}")
        
        return {
            "success": True,
            "note_path": str(note_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Append failed: {e}")
        raise HTTPException(500, f"Failed to append to note: {str(e)}")
```

#### Integration with Polly Init

Update `/core/polly.py` (in `__init__` method after RAG init):

```python
# Initialize deduplication engine
from core.notes_dedup import init_dedup_engine
from core.notes_index import get_notes_index

dedup_engine = init_dedup_engine(self.rag, get_notes_index())
logger.info("Deduplication engine initialized with RAG and NotesIndex")
```

**Testing (Day 1 End):**
- Create note with similar content to existing note
- Verify similarity detection works
- Check threshold sensitivity (70%, 80%, 90%)
- Test with no similar notes
- Test with RAG system disconnected (graceful fallback)

---

### Day 2: UI for Similar Notes Warning (6-8 hours)

#### Morning: HTML Structure

Update `/electron-app/src/renderer/index.html`:

Add to note preview modal (find existing `#note-preview-modal`):

```html
<!-- Add after existing preview content, before action buttons -->
<div id="similar-notes-warning" class="similar-notes-warning hidden">
  <div class="warning-header">
    <i data-lucide="alert-triangle"></i>
    <h4>Similar Notes Found</h4>
  </div>
  
  <p class="warning-text">
    Polly found existing notes that might be related. Consider appending or linking instead of creating a new note.
  </p>
  
  <div id="similar-notes-list" class="similar-notes-list">
    <!-- Populated dynamically by JavaScript -->
  </div>
  
  <div class="warning-actions">
    <button class="btn btn-secondary" id="btn-append-to-similar">
      <i data-lucide="file-plus"></i>
      Append to Selected Note
    </button>
    <button class="btn btn-secondary" id="btn-link-to-similar">
      <i data-lucide="link"></i>
      Create with Links
    </button>
    <button class="btn btn-primary" id="btn-create-anyway">
      <i data-lucide="file-text"></i>
      Create New Note Anyway
    </button>
  </div>
</div>
```

### Day 2: UI for Similar Notes Warning (6-8 hours)

#### Morning: HTML Structure

**Note:** The native notes system uses a **modal for note creation** in the notes view, NOT the old Obsidian preview modal. We need to integrate with the **Create Note Modal** in notes-manager.js.

Update `/electron-app/src/renderer/index.html`:

Find the **Create Note Modal** (search for `id="create-note-modal"`) and add similar notes warning section:

```html
<!-- Add inside #create-note-modal, AFTER the form but BEFORE the buttons -->
<div id="similar-notes-warning" class="similar-notes-warning hidden">
  <div class="warning-header">
    <i data-lucide="alert-triangle"></i>
    <h4>Similar Notes Found</h4>
  </div>
  
  <p class="warning-text">
    Polly found existing notes that might be related. Consider appending or linking instead of creating a new note.
  </p>
  
  <div id="similar-notes-list" class="similar-notes-list">
    <!-- Populated dynamically by JavaScript -->
  </div>
  
  <div class="similar-notes-actions">
    <button type="button" class="btn btn-secondary" id="btn-append-to-similar">
      <i data-lucide="file-plus"></i>
      Append to Selected
    </button>
    <button type="button" class="btn btn-secondary" id="btn-link-to-similar">
      <i data-lucide="link"></i>
      Create with Links
    </button>
    <button type="button" class="btn btn-primary" id="btn-create-anyway">
      <i data-lucide="file-text"></i>
      Create Anyway
    </button>
  </div>
</div>

<!-- Update the existing "Create Note" button to say "Check for Duplicates" -->
<button type="button" class="btn btn-primary" id="btn-check-duplicates">
  Check for Duplicates
</button>
```

#### Afternoon: JavaScript Logic in notes-manager.js

Update `/electron-app/src/renderer/notes-manager.js`:

```javascript
// ===== DEDUPLICATION LOGIC =====

// Global state for similar notes check
let currentSimilarNotes = null;
let proposedNoteData = null;

// Modify the existing createNoteFromModal() function
async function createNoteFromModal() {
    const noteNameInput = document.getElementById('new-note-name');
    const folderSelect = document.getElementById('new-note-folder');
    const contentTextarea = document.getElementById('new-note-content');
    
    const noteName = noteNameInput.value.trim();
    const folder = folderSelect.value;
    const content = contentTextarea.value.trim() || `# ${noteName}\n\n`;
    
    if (!noteName) {
        showNotification('Please enter a note name', 'error');
        return;
    }
    
    // Store proposed note data
    proposedNoteData = {
        name: noteName,
        domain: folder,
        content: content
    };
    
    try {
        // First, check for duplicates
        const response = await fetch('http://localhost:11436/polly/notes/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: noteName,
                domain: folder,
                content: content,
                check_duplicates: true  // Enable duplicate detection
            })
        });
        
        const result = await response.json();
        
        // Check if similar notes were found
        if (result.status === 'similar_found' && result.similar_notes) {
            // Show similar notes warning
            currentSimilarNotes = result.similar_notes;
            showSimilarNotesWarning(result.similar_notes);
            return;  // Don't create yet, wait for user decision
        }
        
        // No similar notes, proceed with creation
        if (result.success) {
            showNotification(`Note "${noteName}" created successfully`);
            closeCreateNoteModal();
            await refreshNotesList();
            
            // Open the newly created note
            if (result.note && result.note.path) {
                loadNoteContent(result.note.path);
            }
        }
    } catch (error) {
        console.error('Create note failed:', error);
        showNotification('Failed to create note', 'error');
    }
}

// Show similar notes warning in the modal
function showSimilarNotesWarning(similarNotes) {
    const warningDiv = document.getElementById('similar-notes-warning');
    const listContainer = document.getElementById('similar-notes-list');
    
    if (!warningDiv || !listContainer) {
        console.error('Similar notes warning elements not found');
        return;
    }
    
    // Clear previous results
    listContainer.innerHTML = '';
    
    // Render each similar note
    similarNotes.forEach((note, index) => {
        const card = document.createElement('div');
        card.className = 'similar-note-card';
        card.dataset.path = note.path;
        
        // Calculate similarity badge style
        const similarityPercent = Math.round(note.similarity * 100);
        const similarityClass = similarityPercent >= 85 ? 'high' : 
                               similarityPercent >= 70 ? 'medium' : 'low';
        
        const noteId = `similar-note-${index}`;
        
        card.innerHTML = `
            <div class="similar-note-header">
                <input type="radio" name="selected-similar-note" value="${note.path}" 
                       id="${noteId}" ${index === 0 ? 'checked' : ''}>
                <label for="${noteId}" class="similar-note-title">
                    <strong>${note.title}</strong>
                </label>
                <span class="similarity-badge similarity-${similarityClass}">
                    ${similarityPercent}%
                </span>
            </div>
            <div class="similar-note-snippet">${note.snippet}</div>
            <div class="similar-note-path">${note.domain} • ${note.name}</div>
        `;
        
        listContainer.appendChild(card);
        
        // Make the entire card clickable to select the radio button
        card.addEventListener('click', (e) => {
            if (e.target.tagName !== 'INPUT') {
                const radio = card.querySelector('input[type="radio"]');
                radio.checked = true;
                // Update visual selection
                document.querySelectorAll('.similar-note-card').forEach(c => 
                    c.classList.remove('selected'));
                card.classList.add('selected');
            }
        });
    });
    
    // Show the warning section
    warningDiv.classList.remove('hidden');
    
    // Hide the "Check for Duplicates" button (already checked)
    const checkButton = document.getElementById('btn-check-duplicates');
    if (checkButton) checkButton.style.display = 'none';
    
    // Scroll warning into view
    warningDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Event handler: Append to selected note
document.getElementById('btn-append-to-similar')?.addEventListener('click', async () => {
    const selected = document.querySelector('input[name="selected-similar-note"]:checked');
    if (!selected) {
        showNotification('Please select a note to append to', 'error');
        return;
    }
    
    const targetPath = selected.value;
    const content = proposedNoteData.content;
    
    try {
        const response = await fetch('http://localhost:11436/polly/notes/append', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                path: targetPath,
                content: content,
                separator: '\n\n---\n\n'  // Horizontal rule separator
            })
        });
        
        if (!response.ok) throw new Error('Append failed');
        
        const result = await response.json();
        
        showNotification(`Content appended to ${targetPath.split('/').pop()}`);
        closeCreateNoteModal();
        
        // Refresh notes list and open the updated note
        await refreshNotesList();
        loadNoteContent(targetPath);
        
    } catch (error) {
        console.error('Failed to append content:', error);
        showNotification('Failed to append content', 'error');
    }
});

// Event handler: Create with links to similar notes
document.getElementById('btn-link-to-similar')?.addEventListener('click', async () => {
    if (!currentSimilarNotes || !proposedNoteData) return;
    
    // Generate wikilinks from similar notes
    const links = currentSimilarNotes
        .slice(0, 5)  // Top 5 most similar
        .map(n => `- [[${n.name}]]`)
        .join('\n');
    
    // Add "Related Notes" section to content
    const updatedContent = proposedNoteData.content + `\n\n## Related Notes\n\n${links}`;
    
    // Create note with updated content (bypass duplicate check)
    try {
        const response = await fetch('http://localhost:11436/polly/notes/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: proposedNoteData.name,
                domain: proposedNoteData.domain,
                content: updatedContent,
                check_duplicates: false  // Skip check, we already handled it
            })
        });
        
        if (!response.ok) throw new Error('Creation failed');
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Note created with ${currentSimilarNotes.length} related links`);
            closeCreateNoteModal();
            await refreshNotesList();
            
            // Open the newly created note
            if (result.note && result.note.path) {
                loadNoteContent(result.note.path);
            }
        }
        
    } catch (error) {
        console.error('Failed to create note:', error);
        showNotification('Failed to create note', 'error');
    }
});

// Event handler: Create note anyway (ignore similar notes)
document.getElementById('btn-create-anyway')?.addEventListener('click', async () => {
    if (!proposedNoteData) return;
    
    try {
        const response = await fetch('http://localhost:11436/polly/notes/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: proposedNoteData.name,
                domain: proposedNoteData.domain,
                content: proposedNoteData.content,
                check_duplicates: false  // Explicitly bypass duplicate check
            })
        });
        
        if (!response.ok) throw new Error('Creation failed');
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Note "${proposedNoteData.name}" created`);
            closeCreateNoteModal();
            await refreshNotesList();
            
            // Open the newly created note
            if (result.note && result.note.path) {
                loadNoteContent(result.note.path);
            }
        }
        
    } catch (error) {
        console.error('Failed to create note:', error);
        showNotification('Failed to create note', 'error');
    }
});

// Update closeCreateNoteModal to reset state
function closeCreateNoteModal() {
    const modal = document.getElementById('create-note-modal');
    if (modal) {
        modal.classList.add('hidden');
        
        // Reset form
        document.getElementById('new-note-name').value = '';
        document.getElementById('new-note-content').value = '';
        
        // Hide similar notes warning
        const warningDiv = document.getElementById('similar-notes-warning');
        if (warningDiv) warningDiv.classList.add('hidden');
        
        // Show check button again
        const checkButton = document.getElementById('btn-check-duplicates');
        if (checkButton) checkButton.style.display = '';
        
        // Reset state
        currentSimilarNotes = null;
        proposedNoteData = null;
    }
}
```

#### CSS Styling

Add to `/electron-app/src/renderer/styles/main.css`:

```css
/* Similar Notes Warning Styles */

.similar-notes-warning {
  background: var(--color-bg-secondary);
  border: 2px solid var(--color-warning, #f59e0b);
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.warning-header i {
  color: var(--color-warning, #f59e0b);
  width: 24px;
  height: 24px;
}

.warning-header h4 {
  margin: 0;
  color: var(--color-warning, #f59e0b);
  font-size: 1.125rem;
}

.warning-text {
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
  line-height: 1.6;
}

.similar-notes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0 1.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.similar-note-card {
  background: var(--color-bg);
  border: 2px solid var(--color-border);
  padding: 1rem;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.similar-note-card:hover {
  border-color: var(--color-accent);
  background: var(--color-bg-hover, rgba(255, 255, 255, 0.05));
}

.similar-note-card:has(input:checked) {
  border-color: var(--color-accent);
  background: var(--color-bg-selected, rgba(59, 130, 246, 0.1));
}

.similar-note-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.similar-note-header input[type="radio"] {
  margin: 0;
  cursor: pointer;
}

.similar-note-title {
  flex: 1;
  font-weight: bold;
  color: var(--color-text);
  cursor: pointer;
}

.similarity-badge {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: bold;
  border-radius: 4px;
}

.similarity-badge.high {
  background: var(--color-error, #ef4444);
  color: white;
}

.similarity-badge.medium {
  background: var(--color-warning, #f59e0b);
  color: black;
}

.similarity-badge.low {
  background: var(--color-info, #3b82f6);
  color: white;
}

.similar-note-snippet {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0.5rem 0;
}

.similar-note-path {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  font-family: var(--font-mono, 'Courier New', monospace);
  opacity: 0.7;
}

.warning-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.warning-actions .btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.warning-actions .btn i {
  width: 16px;
  height: 16px;
}
```

**Testing (Day 2 End):**
- Create note with similar content
- Verify warning displays correctly
- Test "Append to Selected Note" action
- Test "Create with Links" action
- Test "Create New Note Anyway" action
- Verify radio button selection
- Test with no similar notes (warning hidden)
- Test with 1, 3, and 5+ similar notes

---

### Day 3: Polish & Testing (4-6 hours)

#### Morning: Edge Cases & Error Handling

**Edge Cases to Handle:**
1. **No similar notes found:** Return standard success response, no warning shown
2. **All notes are very similar (90%+):** Show strong warning with red badges
3. **RAG system disconnected:** Gracefully skip duplicate check, log warning
4. **Append fails:** Show error notification, allow retry or fallback to create new
5. **Very long note content:** Ensure snippet extraction works correctly
6. **Special characters in note names:** Handle in wikilink generation
7. **NotesIndex not initialized:** Skip duplicate check gracefully

**Error Handling Improvements:**

```python
# In core/notes_dedup.py:

def check_similarity(self, content: str, title: str, similarity_threshold: float = 0.70, max_results: int = 5) -> List[SimilarNote]:
    """Check similarity with robust error handling."""
    
    # Validate inputs
    if not content or not title:
        logger.warning("Empty content or title, skipping duplicate check")
        return []
    
    # Check if RAG is available
    if not self.rag:
        logger.warning("RAG system not available, skipping duplicate check")
        return []
    
    # Check if NotesIndex is available
    if not self.notes_index:
        logger.warning("NotesIndex not available, skipping duplicate check")
        return []
    
    try:
        results = self.rag.search(
            query=f"{title}\n\n{content}",
            n_results=10,
            source_types=['notes']  # Only search notes
        )
        
        similar_notes = []
        
        for result in results:
            try:
                score = result.score
                doc = result.doc
                
                if score >= similarity_threshold:
                    note_path = Path(doc.metadata.get('filepath', ''))
                    note_info = self.notes_index.find_note_by_path(note_path)
                    
                    if note_info:
                        snippet = self._extract_snippet(doc.content, max_length=200)
                        
                        similar_notes.append(SimilarNote(
                            path=str(note_info.path),
                            name=note_info.name,
                            title=note_info.title or note_info.name,
                            domain=note_info.domain or 'Unknown',
                            similarity=score,
                            snippet=snippet
                        ))
            except Exception as e:
                logger.warning(f"Error processing search result: {e}")
                continue  # Skip this result, continue with others
        
        similar_notes.sort(key=lambda x: x.similarity, reverse=True)
        similar_notes = similar_notes[:max_results]
        
        logger.info(f"Found {len(similar_notes)} similar notes for '{title}' (threshold: {similarity_threshold})")
        return similar_notes
        
    except Exception as e:
        logger.error(f"Duplicate check failed: {e}", exc_info=True)
        # Return empty list - dedup is nice-to-have, not blocking
        return []
```

#### Afternoon: Configuration & Final Testing

**Configuration Settings:**

Add to `~/.polly/config.yaml`:

```yaml
# Knowledge Base Deduplication (Phase 21)
deduplication:
  enabled: true
  similarity_threshold: 0.70  # 70% similarity to flag (0.50-0.95)
  max_similar_notes: 5  # Show top N similar notes
```

**Optional: User Settings UI (Future Enhancement)**

Settings could be added to Settings → Notes section to allow users to:
- Enable/disable duplicate detection
- Adjust similarity threshold (50-95%)
- Set max similar notes to display (3-10)

For now, these settings are in config.yaml only.

**Final Testing Checklist:**
- ✅ Duplicate detection works with 70%, 80%, 90% thresholds
- ✅ UI displays correctly with 0, 1, 3, 5+ similar notes
- ✅ Append action works correctly
- ✅ Create with links works correctly
- ✅ Create anyway works correctly
- ✅ Radio button selection works
- ✅ Error handling for RAG disconnection
- ✅ Error handling for append failure
- ✅ Performance: check completes in < 500ms
- ✅ Settings UI for enabling/disabling
- ✅ Settings UI for threshold adjustment
- ✅ No regressions in existing note creation flow
- ✅ Works across all domains
- ✅ Compatible with Phase 16 native notes (forward-compatible)

---

## Files Modified/Created (UPDATED for Native Notes)

### New Files
- `/core/notes_dedup.py` (~300 lines) - Deduplication engine for native notes
  - `SimilarNote` dataclass
  - `DeduplicationEngine` class
  - `check_similarity()` method
  - `suggest_links()` method
  - Global singleton management

### Modified Files
- `/interfaces/server.py` (+180 lines)
  - Update `/polly/notes/create` endpoint with duplicate detection
  - New `/polly/notes/append` endpoint for appending content
  - Integration with dedup engine
- `/core/polly.py` (+10 lines) - Initialize dedup engine in `__init__`
- `/electron-app/src/renderer/index.html` (+80 lines)
  - Add similar notes warning section to Create Note Modal
  - Three action buttons (Append, Link, Create Anyway)
- `/electron-app/src/renderer/notes-manager.js` (+250 lines)
  - `showSimilarNotesWarning()` function
  - `createNoteFromModal()` modified for duplicate detection
  - Event handlers for all three dedup actions
  - State management for similar notes
- `/electron-app/src/renderer/styles/main.css` (+120 lines)
  - `.similar-notes-warning` styles
  - `.similar-note-card` styles with hover/selected states
  - `.similarity-badge` styles (high/medium/low)
  - Responsive layout
- `~/.polly/config.yaml` (+5 lines) - Deduplication settings section

**Total:** ~300 new lines (core/notes_dedup.py), ~645 modified lines

---

## Success Criteria (UPDATED)

- ✅ Similar notes detected before creation (70%+ similarity threshold)
- ✅ Warning UI displays in Create Note Modal with up to 5 similar notes
- ✅ "Append to Selected" action works correctly
  - Appends content to selected note with `---` separator
  - Opens the updated note after append
  - Refreshes notes list
- ✅ "Create with Links" action adds wikilinks to related notes
  - Generates `[[note_name]]` wikilinks for top 5 similar notes
  - Adds "## Related Notes" section to new note
  - Creates note and opens it
- ✅ "Create Anyway" bypasses warning and creates note normally
- ✅ Performance: duplicate check completes in < 500ms
- ✅ Graceful fallback when RAG or NotesIndex unavailable
- ✅ Dedup engine initialized with Polly system
- ✅ No false positives (unrelated notes flagged as similar)
- ✅ No regressions in existing note creation flow
- ✅ Works with native Polly notes system (Phase 16)
- ✅ Compatible with all domains/folders
- ✅ Radio button selection works correctly
- ✅ Modal state resets properly on close

---

## Integration with Other Phases (UPDATED)

**Phase 2 (RAG System):**
- Uses RAG.search() for semantic similarity detection
- Searches only the 'notes' collection
- No changes to RAG system needed

**Phase 16 (Native Notes System):**
- Integrates directly with `/polly/notes/create` endpoint
- Uses NotesIndex for note metadata lookups
- Works seamlessly with existing notes browser UI
- Compatible with note creation modal flow

**Phase 13 (Pattern Learning):**
- Future: Dedup engine could learn which notes users frequently link together
- Suggest related notes based on learned patterns + semantic similarity

**Phase 14 (Mental Models):**
- Future: When creating note about mental model, auto-find related model notes
- Suggest links between related frameworks

**Phase 12 (Knowledge Graph):**
- Future: Similar notes become graph edges (similarity type)
- Visualize note clustering by similarity

---

## Marketing Alignment

**Theme:** "Stop organizing. Start working."

**Message:** Polly prevents knowledge fragmentation by helping you build on existing notes instead of creating duplicates. Your knowledge base stays clean and connected automatically.

**User Benefit:** Less time managing notes, more time using knowledge.

---

## Future Enhancements (Not in v1)

- **Smart merge:** Suggest merging two highly similar notes into one
- **Similarity explanation:** Show which sections/paragraphs are similar
- **Domain-aware thresholds:** Different similarity thresholds per domain
- **Time-based decay:** Older notes less likely to be flagged as similar
- **User feedback loop:** Learn from user's append/ignore decisions

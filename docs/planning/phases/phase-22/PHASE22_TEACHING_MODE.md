# Phase 22: Teaching Mode

**Status:** Not Started  
**Priority:** Medium-High (Tier 1 - Core Intelligence)  
**Estimated Effort:** 2-3 days  
**Complexity:** Medium

**Prerequisites:** 
- Phase 14 (Mental Models) must be complete
- Phase 21 (Knowledge Deduplication) recommended

---

## Executive Summary

Create a specialized "Teaching Mode" that transforms Polly into a Socratic educator focused on deep learning rather than quick answers. When activated, Polly uses progressive difficulty, checks understanding, references prior knowledge, and automatically creates structured learning notes. This mode embodies Freire's pedagogy of liberation: learning as dialogue, not transmission.

## Current State

**What Exists:**
- ✅ Mental models system (Phase 14) - Framework for custom instruction sets
- ✅ Pattern learning (Phase 13) - Tracks learned concepts
- ✅ Knowledge base writing (Phase 3) - Can create notes
- ✅ Conversation history - Can reference prior learning

**The Problem:**
- ❌ No "mode switching" capability
- ❌ No teaching-specific instruction set
- ❌ No Socratic questioning framework
- ❌ No progressive difficulty adjustment
- ❌ No learning path tracking
- ❌ Polly gives direct answers instead of guiding discovery

**Integration Points:**
- `/core/mental_models.py` - Add teaching mode mental model
- `/core/polly.py` - Mode detection and activation
- `/electron-app/src/renderer/index.html` - Mode switcher UI
- `/learners/learning_tracker.py` (NEW) - Track learning progress

---

## User Experience

### Before Teaching Mode

```
User: "How does async/await work in Python?"

Polly: "Async/await in Python allows you to write asynchronous code. 
The async keyword defines a coroutine function, and await pauses 
execution until the awaited coroutine completes. Here's an example:

async def fetch_data():
    response = await http.get('api.example.com')
    return response.json()
"

Result: User gets answer, but doesn't deeply understand
```

### After Teaching Mode (Activated)

```
User: "How does async/await work in Python?"

Polly (Teaching Mode): "Great question! Before we dive into async/await, 
let me check your foundation:

1. What do you already know about how Python normally executes code?
2. Have you encountered situations where your program had to 'wait' 
   for something (like a file read or network request)?
3. What happens to your program during that wait time?"

User: "Well, normally Python runs one line at a time. And yeah, 
when I make an API call, the program just sits there waiting."

Polly: "Perfect! You've identified the key problem. Let's explore 
together: What would be the *ideal* behavior while waiting for that 
API response?"

User: "It could be doing other work?"

Polly: "Exactly! That's what async/await enables. Now, let's build 
this understanding step by step. First, let's talk about what a 
'coroutine' is. Can you guess what that word might mean, based on 
'co-' (together) and '-routine' (function)?"

[Dialogue continues with Socratic guidance]

[After concept is understood]

Polly: "I notice you've grasped the core concepts. Would you like me 
to create a structured note capturing what we learned? I'll include:
- Core concept definition
- Key principles we discovered
- The example we built together
- Related concepts to explore next

Create learning note? [Yes] [No]"

User: [Yes]

Polly: Creates "Learning - Async Await in Python.md" in Scrolls domain
Tags: #learning #python #asynchronous
Links to: [[Concurrency]], [[Event Loops]], [[Coroutines]]
```

---

## Technical Implementation

### Day 1: Teaching Mental Model + Mode Switcher (6-8 hours)

#### Morning: Teaching Mental Model Definition

Update `/core/mental_models.py` (or add default model to `~/.polly/mental_models.yaml`):

```yaml
mental_models:
  - id: teaching_mode
    name: Teaching Mode
    description: |
      Socratic teaching mode for deep learning. Guide the user through 
      discovery rather than giving direct answers. Build on prior knowledge 
      and adapt difficulty progressively.
    
    principles:
      - Ask questions before providing answers (Socratic method)
      - Break complex topics into progressive steps
      - Check understanding before proceeding
      - Connect new concepts to existing knowledge
      - Encourage exploration and experimentation
      - Adapt difficulty based on responses
      - Create structured learning notes automatically
      - Problem-posing over transmission (Freire's pedagogy)
    
    applies_to:
      - sigils    # Teaching code/systems
      - signals   # Teaching audio programming
      - scrolls   # Teaching writing/concepts
      - glyphs    # Teaching design
      - grids     # Teaching frameworks
    
    keywords:
      - teach me
      - explain
      - how do I learn
      - help me understand
      - walk me through
      - I want to learn
      - show me how
    
    prompt_injection: |
      🎓 **TEACHING MODE ACTIVE**
      
      Your role is to be a Socratic educator. Guide discovery, don't transmit information.
      
      ## BEFORE Answering Directly:
      
      1. **Assess Prior Knowledge:**
         - "What do you already know about [topic]?"
         - "Have you encountered [related concept] before?"
         - "What's your experience with [prerequisite]?"
      
      2. **Probe Current Understanding:**
         - Ask questions that reveal their mental model
         - Identify misconceptions gently
         - Build on what they already understand
      
      3. **Guide Discovery (Socratic Method):**
         - Ask leading questions that help them discover the answer
         - "What do you think happens when...?"
         - "How might you solve this problem?"
         - "What's the relationship between X and Y?"
      
      ## PROGRESSIVE DIFFICULTY:
      
      - Start with simple, concrete examples
      - Only introduce complexity after demonstrating understanding
      - Use analogies to familiar concepts
      - Provide examples before abstract theory
      - Build from known → unknown
      
      ## KNOWLEDGE BUILDING:
      
      - Reference previous conversations: "Remember when we learned about...?"
      - Connect to their existing knowledge base
      - Show how this fits into the bigger picture
      - Identify prerequisite knowledge gaps and address them first
      
      ## CHECK UNDERSTANDING:
      
      - Ask them to explain the concept back to you
      - Pose related problems to solve
      - Request examples or analogies from them
      - Only move forward when understanding is demonstrated
      
      ## AUTO-CREATE LEARNING NOTES:
      
      After successfully teaching a concept, offer:
      "I can create a structured learning note capturing what we covered. It will include:
      - Concept definition and core principles
      - Examples we explored together
      - Your key insights and 'aha' moments
      - Related concepts to explore next
      - Practice exercises
      
      Would you like me to create this note?"
      
      ## ADAPTIVE DIFFICULTY:
      
      - If they struggle: Simplify, provide more scaffolding, use more concrete examples
      - If they excel: Increase complexity, introduce edge cases, ask deeper questions
      - Track mastery level (1-5) for each topic
      
      ## FREIRE'S PEDAGOGY PRINCIPLES:
      
      - **Problem-Posing:** Present real problems to solve, not facts to memorize
      - **Dialogue:** Learning is a conversation, not a lecture
      - **Critical Consciousness:** Help them understand *why*, not just *what*
      - **Praxis:** Combine reflection with action (theory + practice)
      - **Co-Creation:** We are learning together, you are not just transmitting
      
      Remember: Your goal is deep understanding, not quick answers. Be patient, 
      encouraging, and adaptive. Celebrate insights and progress.
    
    enabled: false  # User must explicitly activate
    category_triggers: []  # No auto-activation (explicit toggle only)
    created: 2026-01-25T10:00:00
    updated: 2026-01-25T10:00:00
```

#### Afternoon: Mode Switcher UI

Update `/electron-app/src/renderer/index.html`:

Add to conversation header (near existing conversation controls):

```html
<!-- Teaching Mode Toggle -->
<div class="mode-switcher">
  <button 
    class="btn-mode" 
    id="btn-toggle-teaching-mode" 
    title="Teaching Mode - Socratic learning with guided discovery"
    aria-label="Toggle Teaching Mode"
  >
    <i data-lucide="graduation-cap"></i>
    <span class="mode-label">Teaching Mode</span>
  </button>
</div>
```

Update `/electron-app/src/renderer/app.js`:

```javascript
// Mode state
let teachingModeActive = false;
let currentConversationId = null;

// Initialize mode switcher
document.getElementById('btn-toggle-teaching-mode')?.addEventListener('click', async () => {
  teachingModeActive = !teachingModeActive;
  
  const btn = document.getElementById('btn-toggle-teaching-mode');
  if (teachingModeActive) {
    btn.classList.add('active');
    btn.setAttribute('aria-pressed', 'true');
    showNotification('🎓 Teaching Mode activated - Socratic learning enabled', 'info');
    
    // Enable teaching mental model for this conversation
    if (currentConversationId) {
      await window.polly.conversationSetModels(currentConversationId, ['teaching_mode']);
    }
    
    // Show brief explanation tooltip
    showTeachingModeInfo();
  } else {
    btn.classList.remove('active');
    btn.setAttribute('aria-pressed', 'false');
    showNotification('Teaching Mode deactivated', 'info');
    
    // Reset to auto-selection
    if (currentConversationId) {
      await window.polly.conversationSetModels(currentConversationId, null);
    }
  }
});

function showTeachingModeInfo() {
  // Show brief tooltip explaining teaching mode
  const tooltip = document.createElement('div');
  tooltip.className = 'teaching-mode-tooltip';
  tooltip.innerHTML = `
    <div class="tooltip-content">
      <strong>Teaching Mode Active</strong>
      <p>Polly will guide you through discovery using Socratic questioning. 
      Expect questions that help you build understanding, not just direct answers.</p>
    </div>
  `;
  
  document.body.appendChild(tooltip);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    tooltip.classList.add('fade-out');
    setTimeout(() => tooltip.remove(), 300);
  }, 5000);
}

// Track current conversation (for mode persistence)
function onConversationChanged(conversationId) {
  currentConversationId = conversationId;
  
  // Check if this conversation has teaching mode enabled
  window.polly.conversationGetModels(conversationId).then(models => {
    const hasTeachingMode = models && models.includes('teaching_mode');
    teachingModeActive = hasTeachingMode;
    
    const btn = document.getElementById('btn-toggle-teaching-mode');
    if (hasTeachingMode) {
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
    } else {
      btn.classList.remove('active');
      btn.setAttribute('aria-pressed', 'false');
    }
  });
}
```

Add CSS to `/electron-app/src/renderer/styles/main.css`:

```css
/* Teaching Mode Styles */

.mode-switcher {
  display: inline-flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-mode {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-bg-secondary);
  border: 2px solid var(--color-border);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.btn-mode:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
  background: var(--color-bg-hover);
}

.btn-mode.active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: white;
  font-weight: bold;
}

.btn-mode .mode-label {
  display: none;
}

@media (min-width: 768px) {
  .btn-mode .mode-label {
    display: inline;
  }
}

.btn-mode i {
  width: 18px;
  height: 18px;
}

.teaching-mode-tooltip {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  max-width: 300px;
  background: var(--color-bg);
  border: 2px solid var(--color-accent);
  padding: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.teaching-mode-tooltip.fade-out {
  animation: fadeOut 0.3s ease;
  opacity: 0;
}

.tooltip-content strong {
  color: var(--color-accent);
  display: block;
  margin-bottom: 0.5rem;
}

.tooltip-content p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
}

@keyframes slideIn {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}
```

**Testing (Day 1 End):**
- Teaching mode toggle button appears in conversation header
- Clicking activates mode (visual feedback)
- Mode persists across conversation switches
- Mode resets when conversation changes (unless that conversation also has teaching mode)
- Tooltip displays when activated
- Mental model injection works (test with simple query)

---

### Day 2: Learning Path Tracking (6-8 hours)

#### Morning: Learning Tracker Core

Create `/learners/learning_tracker.py`:

```python
"""
Learning Path Tracker
Tracks what the user has learned and suggests next topics
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class LearningTopic:
    """A topic the user is learning."""
    id: str
    title: str
    domain: str
    concepts: List[str]  # Sub-concepts covered
    mastery_level: int  # 1-5 (1=introduced, 3=understood, 5=mastered)
    first_learned: datetime
    last_reviewed: datetime
    notes_created: List[str] = field(default_factory=list)  # File paths
    related_topics: List[str] = field(default_factory=list)  # Topic IDs
    
class LearningTracker:
    """Tracks learning progress and suggests next topics."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.topics: Dict[str, LearningTopic] = {}
        self._load_topics()
    
    def record_learning(
        self,
        title: str,
        domain: str,
        concepts: List[str],
        mastery_level: int = 1,
        note_path: Optional[str] = None
    ):
        """
        Record that user learned a topic.
        
        Args:
            title: Topic title (e.g., "Async/Await in Python")
            domain: Domain ID (sigils, signals, etc.)
            concepts: List of concepts covered
            mastery_level: 1-5 scale (1=introduced, 5=mastered)
            note_path: Path to learning note (if created)
        """
        topic_id = self._make_id(title)
        
        now = datetime.now()
        
        if topic_id in self.topics:
            # Update existing
            topic = self.topics[topic_id]
            topic.concepts.extend(c for c in concepts if c not in topic.concepts)
            topic.mastery_level = max(topic.mastery_level, mastery_level)
            topic.last_reviewed = now
            if note_path and note_path not in topic.notes_created:
                topic.notes_created.append(note_path)
        else:
            # Create new
            topic = LearningTopic(
                id=topic_id,
                title=title,
                domain=domain,
                concepts=concepts,
                mastery_level=mastery_level,
                first_learned=now,
                last_reviewed=now,
                notes_created=[note_path] if note_path else []
            )
            self.topics[topic_id] = topic
        
        self._save_topics()
        logger.info(f"Recorded learning: {title} (mastery: {mastery_level}/5)")
    
    def get_topic(self, title: str) -> Optional[LearningTopic]:
        """Get topic by title."""
        topic_id = self._make_id(title)
        return self.topics.get(topic_id)
    
    def get_next_topics(self, current_topic: str, count: int = 3) -> List[str]:
        """
        Suggest next topics to learn based on current topic.
        
        Args:
            current_topic: Current topic title
            count: Number of suggestions
        
        Returns:
            List of suggested topic titles
        """
        current = self.topics.get(self._make_id(current_topic))
        if not current:
            return []
        
        suggestions = []
        
        # Strategy 1: Related topics with lower mastery
        for related_id in current.related_topics:
            if related_id in self.topics:
                related = self.topics[related_id]
                if related.mastery_level < current.mastery_level:
                    suggestions.append(related.title)
        
        # Strategy 2: Same domain, higher difficulty
        for topic in self.topics.values():
            if (topic.domain == current.domain and 
                topic.mastery_level <= current.mastery_level + 1 and
                topic.id != current.id):
                if topic.title not in suggestions:
                    suggestions.append(topic.title)
        
        return suggestions[:count]
    
    def get_topics_for_review(self, days_since_last_review: int = 7) -> List[LearningTopic]:
        """
        Get topics that should be reviewed (spaced repetition).
        
        Args:
            days_since_last_review: Number of days since last review
        
        Returns:
            List of topics needing review, sorted by last review date
        """
        now = datetime.now()
        review_topics = []
        
        for topic in self.topics.values():
            days_since = (now - topic.last_reviewed).days
            
            # Spaced repetition intervals based on mastery
            review_interval = {
                1: 1,   # Introduced: review after 1 day
                2: 3,   # Learning: review after 3 days
                3: 7,   # Understood: review after 1 week
                4: 14,  # Proficient: review after 2 weeks
                5: 30   # Mastered: review after 1 month
            }.get(topic.mastery_level, 7)
            
            if days_since >= review_interval:
                review_topics.append(topic)
        
        # Sort by last reviewed (oldest first)
        return sorted(review_topics, key=lambda t: t.last_reviewed)
    
    def get_learning_stats(self) -> Dict:
        """Get overall learning statistics."""
        total_topics = len(self.topics)
        by_domain = {}
        by_mastery = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for topic in self.topics.values():
            # Count by domain
            by_domain[topic.domain] = by_domain.get(topic.domain, 0) + 1
            
            # Count by mastery level
            by_mastery[topic.mastery_level] += 1
        
        return {
            "total_topics": total_topics,
            "by_domain": by_domain,
            "by_mastery": by_mastery,
            "topics_needing_review": len(self.get_topics_for_review())
        }
    
    def _make_id(self, title: str) -> str:
        """Create ID from title."""
        return title.lower().replace(' ', '_').replace('/', '_')
    
    def _load_topics(self):
        """Load learning topics from storage."""
        if not self.storage_path.exists():
            logger.info("No existing learning data, starting fresh")
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            for topic_data in data.get('topics', []):
                topic = LearningTopic(
                    id=topic_data['id'],
                    title=topic_data['title'],
                    domain=topic_data['domain'],
                    concepts=topic_data['concepts'],
                    mastery_level=topic_data['mastery_level'],
                    first_learned=datetime.fromisoformat(topic_data['first_learned']),
                    last_reviewed=datetime.fromisoformat(topic_data['last_reviewed']),
                    notes_created=topic_data.get('notes_created', []),
                    related_topics=topic_data.get('related_topics', [])
                )
                self.topics[topic.id] = topic
            
            logger.info(f"Loaded {len(self.topics)} learning topics")
        except Exception as e:
            logger.error(f"Failed to load learning topics: {e}")
            self.topics = {}
    
    def _save_topics(self):
        """Save learning topics to storage."""
        data = {
            'topics': [
                {
                    'id': t.id,
                    'title': t.title,
                    'domain': t.domain,
                    'concepts': t.concepts,
                    'mastery_level': t.mastery_level,
                    'first_learned': t.first_learned.isoformat(),
                    'last_reviewed': t.last_reviewed.isoformat(),
                    'notes_created': t.notes_created,
                    'related_topics': t.related_topics
                }
                for t in self.topics.values()
            ],
            'version': '1.0',
            'last_updated': datetime.now().isoformat()
        }
        
        self.storage_path.write_text(json.dumps(data, indent=2))
        logger.info(f"Saved {len(self.topics)} learning topics")
```

#### Afternoon: Integration with Polly

Update `/core/polly.py`:

```python
# Add import
from learners.learning_tracker import LearningTracker

# In Polly.__init__:
def __init__(self, config: Dict):
    # ... existing init ...
    
    # Initialize learning tracker
    tracker_path = Path(config.get("learning.storage_path", "~/.polly/learning.json")).expanduser()
    self.learning_tracker = LearningTracker(tracker_path)
    logger.info(f"Learning tracker initialized: {len(self.learning_tracker.topics)} topics tracked")

# Add method to detect if teaching mode is active
def _is_teaching_mode_active(self, conversation_id: Optional[str] = None) -> bool:
    """Check if teaching mode is active for current conversation."""
    if not conversation_id:
        return False
    
    # Check conversation's active mental models
    # (This requires conversation-manager integration)
    models = self.get_conversation_models(conversation_id)
    return 'teaching_mode' in models if models else False

# Add method to create learning note
async def create_learning_note(
    self,
    topic: str,
    content: str,
    concepts: List[str],
    domain: str,
    conversation_id: Optional[str] = None
) -> Dict:
    """
    Create a structured learning note.
    
    Args:
        topic: Topic title
        content: Note content (generated by LLM)
        concepts: List of concepts covered
        domain: Domain ID
        conversation_id: Current conversation ID
    
    Returns:
        Note creation result
    """
    note_title = f"Learning - {topic}"
    
    # Generate structured content
    structured_content = f"""# {topic}

## Key Concepts

{chr(10).join(f"- {c}" for c in concepts)}

## Understanding

{content}

## Related Topics

<!-- Links to related concepts will be added here -->

## Practice Exercises

<!-- Add exercises to reinforce learning -->

---

*Learned: {datetime.now().strftime('%Y-%m-%d')}*  
*Domain: {domain}*  
*Mastery Level: 1/5 (Introduced)*
"""
    
    # Create note via Obsidian integration
    result = await self.obsidian.create_note(
        title=note_title,
        content=structured_content,
        folder=None,  # Auto-suggest based on domain
        tags=['learning', domain],
        preview=False
    )
    
    # Record in learning tracker
    if result.get('status') == 'success':
        self.learning_tracker.record_learning(
            title=topic,
            domain=domain,
            concepts=concepts,
            mastery_level=1,
            note_path=result.get('note_path')
        )
        logger.info(f"Learning note created: {note_title}")
    
    return result
```

Add to `/config.yaml`:

```yaml
# Learning Tracker
learning:
  storage_path: "~/.polly/learning.json"
  spaced_repetition: true
  auto_suggest_review: true
```

**Testing (Day 2 End):**
- Learning tracker initializes correctly
- Can record learning topic
- Can retrieve topic by title
- Spaced repetition intervals work correctly
- Learning stats accurate
- Learning note creation works
- Note includes proper frontmatter and structure

---

### Day 3: Polish & API Integration (4-6 hours)

#### Morning: API Endpoints

Update `/interfaces/server.py`:

```python
# Learning Tracker Endpoints

@app.get("/polly/learning/stats")
async def get_learning_stats():
    """Get overall learning statistics."""
    stats = polly.learning_tracker.get_learning_stats()
    return stats

@app.get("/polly/learning/topics")
async def list_learning_topics():
    """List all learning topics."""
    topics = list(polly.learning_tracker.topics.values())
    return {
        "topics": [
            {
                "id": t.id,
                "title": t.title,
                "domain": t.domain,
                "concepts": t.concepts,
                "mastery_level": t.mastery_level,
                "first_learned": t.first_learned.isoformat(),
                "last_reviewed": t.last_reviewed.isoformat(),
                "notes_created": t.notes_created
            }
            for t in topics
        ]
    }

@app.get("/polly/learning/review")
async def get_topics_for_review():
    """Get topics that need review."""
    topics = polly.learning_tracker.get_topics_for_review()
    return {
        "topics": [
            {
                "title": t.title,
                "domain": t.domain,
                "mastery_level": t.mastery_level,
                "days_since_review": (datetime.now() - t.last_reviewed).days
            }
            for t in topics
        ]
    }

@app.post("/polly/learning/create-note")
async def create_learning_note_endpoint(data: Dict):
    """Create a learning note from conversation."""
    result = await polly.create_learning_note(
        topic=data['topic'],
        content=data['content'],
        concepts=data['concepts'],
        domain=data['domain'],
        conversation_id=data.get('conversation_id')
    )
    return result
```

#### Afternoon: UI Polish & Teaching Mode Enhancements

**Add "Create Learning Note" button** in conversation interface (appears when teaching mode active):

```html
<!-- Add to message actions -->
<button 
  class="btn-action" 
  id="btn-create-learning-note" 
  title="Save as Learning Note"
  style="display: none;"
>
  <i data-lucide="book-open"></i>
  Save Learning Note
</button>
```

```javascript
// Show "Create Learning Note" button when teaching mode active
function updateTeachingModeUI() {
  const btn = document.getElementById('btn-create-learning-note');
  if (teachingModeActive) {
    btn.style.display = 'inline-flex';
  } else {
    btn.style.display = 'none';
  }
}

// Handler for creating learning note
document.getElementById('btn-create-learning-note')?.addEventListener('click', async () => {
  // Extract topic and concepts from conversation
  // (This would require more sophisticated extraction logic)
  
  const topic = prompt('Enter topic title (e.g., "Async/Await in Python"):');
  if (!topic) return;
  
  const concepts = prompt('Enter key concepts (comma-separated):');
  const conceptList = concepts ? concepts.split(',').map(c => c.trim()) : [];
  
  // Get current conversation messages as content
  const messages = document.querySelectorAll('.message');
  const content = Array.from(messages)
    .map(m => m.textContent)
    .join('\n\n');
  
  try {
    const response = await fetch('http://localhost:11436/polly/learning/create-note', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        topic,
        content,
        concepts: conceptList,
        domain: currentDomain || 'scrolls',
        conversation_id: currentConversationId
      })
    });
    
    if (!response.ok) throw new Error('Failed to create note');
    
    const result = await response.json();
    showNotification(`Learning note created: ${result.note_path}`);
  } catch (error) {
    console.error('Failed to create learning note:', error);
    showNotification('Failed to create learning note', 'error');
  }
});
```

**Add Learning Stats Panel** to dashboard:

```html
<!-- Add to dashboard -->
<div class="stats-card learning-stats">
  <h3>
    <i data-lucide="graduation-cap"></i>
    Learning Progress
  </h3>
  
  <div class="stat-row">
    <span class="stat-label">Topics Learned:</span>
    <span class="stat-value" id="topics-learned">0</span>
  </div>
  
  <div class="stat-row">
    <span class="stat-label">Needs Review:</span>
    <span class="stat-value" id="topics-review">0</span>
  </div>
  
  <div class="mastery-breakdown">
    <h4>Mastery Levels</h4>
    <div class="mastery-bar">
      <div class="mastery-segment" data-level="1" style="width: 0%">1</div>
      <div class="mastery-segment" data-level="2" style="width: 0%">2</div>
      <div class="mastery-segment" data-level="3" style="width: 0%">3</div>
      <div class="mastery-segment" data-level="4" style="width: 0%">4</div>
      <div class="mastery-segment" data-level="5" style="width: 0%">5</div>
    </div>
  </div>
</div>
```

```javascript
// Load learning stats
async function loadLearningStats() {
  try {
    const response = await fetch('http://localhost:11436/polly/learning/stats');
    const stats = await response.json();
    
    document.getElementById('topics-learned').textContent = stats.total_topics;
    document.getElementById('topics-needing-review').textContent = stats.topics_needing_review;
    
    // Update mastery breakdown
    const total = stats.total_topics || 1;
    for (let level = 1; level <= 5; level++) {
      const count = stats.by_mastery[level] || 0;
      const percent = (count / total) * 100;
      const segment = document.querySelector(`.mastery-segment[data-level="${level}"]`);
      segment.style.width = `${percent}%`;
      segment.textContent = count > 0 ? count : '';
    }
  } catch (error) {
    console.error('Failed to load learning stats:', error);
  }
}

// Refresh stats periodically
setInterval(loadLearningStats, 60000); // Every minute
```

**Final Testing Checklist:**
- ✅ Teaching mode toggle works
- ✅ Mode persists per conversation
- ✅ Mental model injection works (Socratic questioning)
- ✅ Learning tracker records topics correctly
- ✅ Spaced repetition intervals accurate
- ✅ Learning note creation works
- ✅ Note structure includes concepts, exercises, related topics
- ✅ Learning stats display correctly
- ✅ "Create Learning Note" button appears in teaching mode
- ✅ Mastery levels tracked correctly (1-5)
- ✅ API endpoints work correctly
- ✅ No regressions in normal conversation mode

---

## Files Modified/Created

### New Files
- `/learners/learning_tracker.py` (~250 lines) - Learning path tracker
- `~/.polly/learning.json` (storage) - Learning topics data

### Modified Files
- `/core/mental_models.py` (+60 lines) - Add teaching mode model
- `/core/polly.py` (+150 lines) - Learning tracker integration
- `/interfaces/server.py` (+60 lines) - Learning API endpoints
- `/electron-app/src/renderer/index.html` (+100 lines) - Mode switcher + learning stats UI
- `/electron-app/src/renderer/app.js` (+180 lines) - Mode toggle + learning note creation
- `/electron-app/src/renderer/styles/main.css` (+120 lines) - Teaching mode styles
- `/config.yaml` (+4 lines) - Learning tracker config

**Total:** ~310 new lines, ~674 modified lines

---

## Success Criteria

- ✅ Teaching mode can be toggled per conversation
- ✅ Polly uses Socratic questioning when in teaching mode
- ✅ Progressive difficulty adjustment based on responses
- ✅ References prior knowledge from conversation history
- ✅ Checks understanding before proceeding
- ✅ Learning topics tracked with mastery levels (1-5)
- ✅ Spaced repetition review suggestions
- ✅ Automatic learning note creation
- ✅ Notes include: concepts, understanding, related topics, practice exercises
- ✅ Learning stats dashboard shows progress
- ✅ Mode persists per conversation
- ✅ No regressions in normal mode

---

## Integration with Other Phases

**Phase 14 (Mental Models):**
- Teaching mode is implemented as a mental model
- Uses mental model injection system for instructions

**Phase 13 (Pattern Learning):**
- Can track which teaching strategies work best
- Learn optimal difficulty progression per user

**Phase 21 (Deduplication):**
- Learning notes automatically linked to related existing notes
- Prevents duplicate learning notes

**Phase 16 (Native Notes):**
- Learning notes stored in native notes system
- Tagged with #learning for easy filtering
- Backlinks between related learning topics

**Phase 12 (Knowledge Graph):**
- Learning topics become graph nodes
- Visualize learning path and connections
- "Explore from here" suggests related topics to learn

---

## Marketing Alignment

**Theme:** "Polly teaches you as you teach Polly"

**Message:** Learning as dialogue, not transmission. Polly guides discovery using Socratic method, adapts to your pace, and builds on your existing knowledge. Knowledge compounds over time through spaced repetition and progressive mastery.

**User Benefit:** Deep understanding, not just quick answers. Build capability that lasts.

**Differentiator vs. ChatGPT/Claude:** They give answers. Polly teaches you to think.

---

## Future Enhancements (Not in v1)

- **Adaptive difficulty AI:** ML model learns optimal difficulty per user
- **Voice teaching mode:** Audio-based Socratic dialogue
- **Collaborative learning:** Share learning paths with others
- **Gamification:** Badges, streaks, achievement system
- **Learning challenges:** Daily practice problems
- **Concept dependency tree:** Visual map of prerequisite knowledge
- **Export learning path:** Share your learning journey as blog post
- **Integration with spaced repetition apps:** Anki, RemNote export

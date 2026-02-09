# Process: Updating Context-Aware Persona System

## Overview

When you add new personas or expand existing persona capabilities, you'll need to update the context-aware detection system so Polly can intelligently suggest them to users.

**Location:** This is a **frontend-only** configuration change in most cases.

---

## Step-by-Step Process

### Step 1: Add New Persona to Pattern Mapping

**File:** `/Users/brettgershon/polly/electron-app/src/renderer/app.js`  
**Location:** Search for `PERSONA_INTENT_PATTERNS` (around line 8762)

**Add your new persona:**

```javascript
const PERSONA_INTENT_PATTERNS = {
  scribe: {
    name: 'Scribe',
    icon: '📝',
    description: 'Transform conversations into structured notes',
    patterns: [ /* existing patterns */ ]
  },
  architect: {
    name: 'Architect',
    icon: '📐',
    description: 'Plan and build complex tasks',
    patterns: [ /* existing patterns */ ]
  },
  
  // ADD NEW PERSONA HERE:
  librarian: {
    name: 'Librarian',                              // Display name in dialog
    icon: '📚',                                       // Emoji icon
    description: 'Search and manage knowledge base', // 1-2 sentence description
    patterns: [
      // Add regex patterns that should trigger this persona
      /\bsearch\s+(for|my)\b/i,                     // "search for" or "search my"
      /\bfind\s+(notes?|documents?)\b/i,            // "find notes" or "find document"
      /\blook\s+up\b/i,                             // "look up"
      /\bwhat\s+do\s+I\s+have\s+(on|about)\b/i,    // "what do I have on..."
      /\bquery\s+(my\s+)?(knowledge|vault)\b/i,     // "query my knowledge"
      /\bshow\s+me\s+(all|my)\s+notes\b/i          // "show me all notes"
    ]
  },
  
  programmer: {
    name: 'Programmer',
    icon: '💻',
    description: 'Write, debug, and refactor code',
    patterns: [
      /\b(write|generate|create)\s+(some\s+)?code\b/i,
      /\b(fix|debug|solve)\s+(this|the|a)\s+(bug|error|issue)\b/i,
      /\brefactor\s+(this|the|my)\s+code\b/i,
      /\bimplement\s+(a|an|the)\s+\w+\s+(function|class|component)\b/i,
      /\breview\s+(this|the|my)\s+code\b/i,
      /\boptimize\s+(this|the)\s+\w+\b/i
    ]
  }
};
```

---

### Step 2: Design Your Patterns

**Pattern Design Guidelines:**

#### Use Word Boundaries (`\b`)
```javascript
/\bsearch\b/i      // ✅ Matches "search" as whole word
/search/i          // ❌ Also matches "researcher", "searching" (too broad)
```

#### Match Common Variations
```javascript
/\b(create|make|generate|build)\s+/i  // Multiple verbs
/\bnotes?\b/i                         // "note" OR "notes"
/\b(a|an|the)\s+guide\b/i            // Optional articles
```

#### Be Specific Enough to Avoid False Positives
```javascript
// ❌ TOO BROAD - triggers on everything:
/\bhelp\b/i

// ✅ BETTER - specific task:
/\bhelp\s+me\s+(write|create|build)\b/i
```

#### Test Pattern Combos
```javascript
// User might say different things:
/\bmake\s+a\s+note\b/i              // "make a note"
/\btake\s+notes\b/i                 // "take notes"
/\bcreate\s+some\s+notes?\b/i       // "create some notes"
/\bsave\s+this\s+as\s+a\s+note\b/i  // "save this as a note"
```

#### Use Case-Insensitive Flag (`/i`)
```javascript
/\bSearch\b/    // ❌ Only matches "Search"
/\bsearch\b/i   // ✅ Matches "search", "Search", "SEARCH"
```

---

### Step 3: Test Your Patterns

**Quick Regex Testing:**

```javascript
// Test in browser console or Node.js:
const pattern = /\bsearch\s+(for|my)\b/i;

// Should match:
console.log(pattern.test("search for notes"));      // true
console.log(pattern.test("Search my documents"));   // true

// Should NOT match:
console.log(pattern.test("researcher notes"));      // false
console.log(pattern.test("I'm searching"));         // false
```

**Test in Polly:**

1. Restart Polly
2. Type queries that should trigger your persona
3. Check console for: `[Persona Intent] Detected <persona> intent: <query>`
4. Verify dialog appears with correct persona
5. Test edge cases and variations

---

### Step 4: Update Persona Dropdown (if needed)

**Only needed if persona is brand new and not in the dropdown yet.**

**File:** `/Users/brettgershon/polly/electron-app/src/renderer/index.html`  
**Location:** Search for `persona-select` (around line 2100-2200)

```html
<select id="persona-select" class="persona-selector">
  <option value="">Default</option>
  <option value="architect">Architect</option>
  <option value="scribe">Scribe</option>
  <!-- ADD NEW OPTION: -->
  <option value="librarian">Librarian</option>
  <option value="programmer">Programmer</option>
</select>
```

**Note:** If the persona already exists in the dropdown, skip this step.

---

### Step 5: Document Your Patterns

**Update:** `/Users/brettgershon/polly/CONTEXT_AWARE_PERSONA_SYSTEM.md`

Add your persona to the "Persona Intent Patterns" section:

```markdown
### Librarian 📚
**Purpose:** Search and manage your knowledge base

**Trigger Patterns:**
- "search for..."
- "find notes"
- "look up..."
- "what do I have on..."
- "query my knowledge"
- "show me all notes"

**Example Queries:**
- ✅ "Search for notes about Docker"
- ✅ "Find all documents about React"
- ✅ "What do I have on machine learning?"
- ✅ "Query my vault for Python tutorials"
```

---

### Step 6: Handle Mode-Specific Actions (Advanced)

**When to use:** If your persona has multiple modes and certain keywords should activate specific modes.

**Current limitation:** The system only activates the persona's **default mode**. It doesn't detect which mode to use.

**Future enhancement idea:**

```javascript
const PERSONA_INTENT_PATTERNS = {
  scribe: {
    name: 'Scribe',
    icon: '📝',
    description: 'Transform conversations into structured notes',
    default_mode: 'capture',  // Activates this mode by default
    
    // Mode-specific patterns (future feature):
    mode_patterns: {
      capture: [/\bsave\s+conversation\b/i],
      edit: [/\bedit\s+(this|my)\s+note\b/i],
      organize: [/\borganize\s+(my\s+)?notes\b/i]
    },
    
    // Fallback patterns (trigger persona, use default_mode):
    patterns: [ /* existing patterns */ ]
  }
};
```

**To implement mode detection:**
1. Add `mode_patterns` to persona config
2. Update `detectPersonaIntent()` to return `{persona, mode}`
3. Update `switchToPersona()` to accept mode parameter
4. Update dialog to show "Switch to Scribe (Edit mode)?"

**For now:** Persona activates in default mode, user can manually switch modes after activation.

---

## Common Patterns Library

### Action Verbs
```javascript
// Creating/Making
/\b(create|make|generate|build|draft|write)\s+/i

// Saving/Capturing
/\b(save|capture|record|log|store|remember)\s+/i

// Finding/Searching
/\b(search|find|look\s+up|query|locate)\s+/i

// Editing/Modifying
/\b(edit|modify|update|change|revise|fix)\s+/i

// Analyzing
/\b(analyze|review|examine|check|inspect)\s+/i
```

### Object Targets
```javascript
// Notes/Documents
/\b(note|notes|document|documents|guide|tutorial|article)\b/i

// Code
/\b(code|function|class|component|module|script)\b/i

// Conversations
/\b(conversation|chat|discussion|meeting)\b/i

// Knowledge
/\b(knowledge|vault|library|database)\b/i
```

### Combining Patterns
```javascript
// Verb + Object + Context
/\b(create|make)\s+a\s+(note|document)\s+(about|on|for)\b/i
// Matches: "create a note about...", "make a document on..."

// Possessive + Object
/\b(this|my|our)\s+(conversation|meeting|discussion)\b/i
// Matches: "this conversation", "my meeting"

// Optional Articles
/\b(save|create)\s+(a\s+|an\s+|the\s+)?(note|guide)\b/i
// Matches: "save note", "save a note", "save the note"
```

---

## Testing Checklist

When adding/updating persona patterns:

### Positive Tests (Should Trigger)
- [ ] Test exact pattern match
- [ ] Test with different word order
- [ ] Test with synonyms
- [ ] Test with extra words
- [ ] Test with mixed case
- [ ] Test with punctuation

### Negative Tests (Should NOT Trigger)
- [ ] Test similar but different queries
- [ ] Test partial word matches
- [ ] Test other persona patterns (ensure no overlap)
- [ ] Test general questions
- [ ] Test ambiguous queries

### Dialog Tests
- [ ] Persona name displays correctly
- [ ] Icon shows properly
- [ ] Description is clear
- [ ] User query is quoted correctly
- [ ] Buttons work as expected
- [ ] Escape key closes dialog
- [ ] Clicking outside closes dialog

### Integration Tests
- [ ] Persona activates after switch
- [ ] Mode selector populates correctly
- [ ] Message processes through persona
- [ ] No console errors
- [ ] Works from floating chat bar
- [ ] Works from sidebar

---

## Troubleshooting

### Pattern Not Triggering

**Check:**
```javascript
// Test your pattern in console:
const pattern = /your-pattern-here/i;
console.log(pattern.test("your test query"));
```

**Common issues:**
- Missing word boundaries (`\b`)
- Case-sensitive (missing `/i` flag)
- Too specific (won't match variations)
- Typo in regex syntax

### Wrong Persona Suggested

**Check pattern order:**
Patterns are checked in order. If multiple personas match, first match wins.

**Solution:**
- Make patterns more specific
- Reorder personas (put more specific ones first)
- Add negative lookaheads to exclude patterns

### Dialog Shows Too Often

**Solutions:**
- Make patterns more restrictive
- Add more specific context requirements
- Consider adding "don't show again" option (future feature)

### Pattern Conflicts

**Multiple personas match the same query:**

```javascript
// ❌ CONFLICT:
scribe: [/\bcreate\s+a\s+note\b/i]
architect: [/\bcreate\s+a\s+note\b/i]

// ✅ RESOLVED - Make them distinct:
scribe: [/\b(save|capture|make)\s+a\s+note\b/i]        // Quick save
architect: [/\bcreate\s+a\s+note\s+(about|on)\b/i]     // Structured creation
```

---

## Examples: Real-World Persona Additions

### Example 1: Adding "Professor" Persona

**Purpose:** Teaching and explaining concepts

```javascript
professor: {
  name: 'Professor',
  icon: '👨‍🏫',
  description: 'Teach and explain concepts in depth',
  patterns: [
    /\b(explain|teach|show)\s+me\s+(how|what|why)\b/i,
    /\bwhat\s+is\s+(a|an|the)?\s*\w+\??$/i,
    /\bhow\s+does\s+\w+\s+work\b/i,
    /\bELI5\b/i,  // Explain Like I'm 5
    /\bbreak\s+down\b/i,
    /\bwalk\s+me\s+through\b/i
  ]
}
```

**Test queries:**
- ✅ "Explain how React hooks work"
- ✅ "What is a closure?"
- ✅ "Teach me about async/await"
- ✅ "ELI5: quantum computing"

---

### Example 2: Adding "Administrator" Persona

**Purpose:** Task and calendar management

```javascript
administrator: {
  name: 'Administrator',
  icon: '📅',
  description: 'Manage tasks, calendar, and reminders',
  patterns: [
    /\b(schedule|add|create)\s+(a|an)?\s*(meeting|appointment|event)\b/i,
    /\b(remind|reminder)\s+me\s+(to|about)\b/i,
    /\b(add|create)\s+a\s+task\b/i,
    /\bwhat'?s\s+on\s+my\s+(calendar|schedule)\b/i,
    /\bset\s+(a|an)?\s*(timer|alarm|reminder)\b/i,
    /\bwhen\s+is\s+my\s+next\b/i
  ]
}
```

**Test queries:**
- ✅ "Schedule a meeting tomorrow at 3pm"
- ✅ "Remind me to call John"
- ✅ "Add a task to review PR"
- ✅ "What's on my calendar today?"

---

### Example 3: Updating Existing Persona (Scribe)

**Scenario:** Users are saying "jot this down" but it's not triggering Scribe.

**Solution:** Add pattern to existing persona:

```javascript
scribe: {
  name: 'Scribe',
  icon: '📝',
  description: 'Transform conversations into structured notes',
  patterns: [
    // ... existing patterns ...
    /\bjot\s+(this|that|it)\s+down\b/i,  // ADD THIS
    /\bquick\s+note\b/i                   // AND THIS
  ]
}
```

**Test:**
- ✅ "Jot this down for me"
- ✅ "Quick note about meeting"

---

## Pattern Design Philosophy

### Be Conservative at First
Start with **specific patterns** that you're confident about. You can always add more later.

```javascript
// ✅ START HERE (specific):
/\bmake\s+a\s+note\s+about\b/i

// ADD LATER if needed (broader):
/\bmake\s+a\s+note\b/i
/\bnote\s+this\b/i
```

### Prefer False Negatives Over False Positives
It's better to **miss some triggers** (user doesn't see dialog) than to **show dialog too often** (annoying).

**Why?**
- User can still manually select persona
- False positives train users to ignore dialogs
- You can add patterns based on real usage

### Use Real User Queries
When possible, base patterns on **actual things users say**, not what you think they'll say.

**How:**
1. Monitor console logs for queries
2. Track queries that should have triggered but didn't
3. Add patterns to catch those cases
4. Test with real usage patterns

---

## Summary Checklist

When adding/updating persona patterns:

- [ ] Add persona to `PERSONA_INTENT_PATTERNS` in `app.js`
- [ ] Design patterns (specific, case-insensitive, word boundaries)
- [ ] Test patterns in console
- [ ] Test in Polly with various queries
- [ ] Update persona dropdown in `index.html` (if new persona)
- [ ] Document patterns in `CONTEXT_AWARE_PERSONA_SYSTEM.md`
- [ ] Run full testing checklist
- [ ] Monitor usage and refine patterns

---

## Quick Reference

**Files to modify:**
1. **`app.js`** (line ~8762) - Add patterns to `PERSONA_INTENT_PATTERNS`
2. **`index.html`** (line ~2100) - Add option to persona dropdown (if new)
3. **`CONTEXT_AWARE_PERSONA_SYSTEM.md`** - Document your patterns

**Pattern syntax:**
```javascript
/\bpattern\b/i
// \b = word boundary
// /i = case insensitive
```

**Test command:**
```javascript
const pattern = /your-pattern/i;
console.log(pattern.test("test query"));
```

**Restart Polly:**
```bash
cd /Users/brettgershon/polly/electron-app
npm start
```

---

**That's it!** Follow this process each time you add a new persona or expand persona capabilities, and the context-aware system will stay up-to-date. 🚀

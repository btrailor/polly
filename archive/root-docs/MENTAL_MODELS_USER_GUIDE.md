# Mental Models System - User Guide

**Phase 14 Feature - Completed January 29, 2026**

---

## What Are Mental Models?

Mental models are frameworks, philosophies, and thinking patterns that guide how Polly responds to you. They're like lenses through which Polly interprets your questions and shapes its answers.

For example:
- **Infinite Games:** Emphasizes continuation over completion, evolving systems
- **Socratic Method:** Uses questions to guide discovery rather than giving direct answers
- **Systems Thinking:** Considers interconnections and second-order effects

Polly comes with 12 default mental models, and you can create unlimited custom ones.

---

## How Mental Models Activate

Mental models automatically activate based on **three-tier context**:

### 1. Domain-Level (Content Type)
Models activate based on what you're working with:
- **Scrolls** (writing/notes) → Pedagogy models
- **Sigils** (code) → Technical models
- **Signals** (audio) → Creative models
- **Glyphs** (design) → Design thinking models
- **Grids** (systems) → Systems thinking models

### 2. Page-Level (Current Workspace)
Models activate based on where you are in Polly:
- **Learning page** → Learning frameworks
- **Code page** → Technical models
- **Mail page** → Communication models (future)
- **Calendar page** → Time management models (future)

### 3. Persona-Level (AI Mode)
Models activate based on which persona you're using:
- **Architect persona** → Systems and technical models
- **Teacher persona** → Pedagogical models (future)

Polly scores all models against your current context and activates the **top 3-5 most relevant** for each query.

---

## Managing Mental Models

### Accessing Settings

1. Open Polly
2. Click **Settings** (⚙️) in the sidebar
3. Click the **Mental Models** tab

You'll see a grid of all your mental models with:
- **Model name and ID**
- **Description**
- **Activation tags** (color-coded by type)
- **Toggle switch** (enable/disable)
- **Edit and Delete buttons**

### Viewing Model Details

Each model card shows:
- 🔵 **Blue tags:** Domains (sigils, scrolls, etc.)
- 🟣 **Purple tags:** Pages (learning, code, etc.)
- 🟡 **Orange tags:** Modes (plan, build, etc.)
- 🩷 **Pink tags:** Personas (architect, teacher)

### Enabling/Disabling Models

Click the **toggle switch** on any model card to enable or disable it instantly.

Disabled models:
- Won't activate automatically
- Won't appear in override menus
- Are visually dimmed in the settings

---

## Creating Custom Mental Models

### Option 1: Start from Template (Recommended)

1. Click **Add Model** button
2. Select a template from the dropdown:
   - **Learning Framework** - For pedagogical approaches
   - **Creative Process** - For creative workflows
   - **Productivity System** - For task management
   - **Systems Approach** - For complex systems
   - **Communication Style** - For communication patterns
3. The form auto-fills with example values
4. Customize as needed
5. Click **Save Model**

### Option 2: Build from Scratch

1. Click **Add Model** button
2. Leave template dropdown on "Blank"
3. Fill in all required fields:

**Required Fields:**
- **ID:** Unique identifier (lowercase_with_underscores)
- **Name:** Display name
- **Description:** What this model represents
- **Principles:** One per line, 3-5 principles
- **Prompt Injection:** How Polly should apply this model

**Activation Context (Optional):**
- **Domains:** Check which content types should trigger this model
- **Pages:** Check which workspaces should trigger this model
- **Personas:** Check which AI personas should use this model
- **Modes:** Check which specific modes should trigger this model

**Optional Fields:**
- **Keywords:** Comma-separated words that trigger this model
- **Enabled:** Whether the model is active (default: checked)

4. Click **Save Model**

### Example Custom Model

```yaml
ID: pomodoro_technique
Name: Pomodoro Technique
Description: Time management using 25-minute focus blocks
Principles:
  - Work in focused 25-minute intervals
  - Take 5-minute breaks between pomodoros
  - Take longer breaks after 4 pomodoros
Prompt Injection: When discussing time management or productivity, 
  suggest breaking work into 25-minute focused intervals with short breaks.
Domains: [grids]
Pages: [projects, calendar]
Keywords: time, focus, productivity, break
```

---

## Editing and Deleting Models

### Editing a Model

1. Click the **Edit** button on any model card
2. Make your changes in the modal
3. Click **Save Model**

**Note:** You cannot change the ID of an existing model. To change an ID, delete and recreate the model.

### Deleting a Model

1. Click the **Delete** button on any model card
2. Confirm the deletion

**Warning:** Deletion cannot be undone. The model will be removed from all conversations.

---

## Per-Conversation Override

Sometimes you want specific models for a particular conversation, regardless of automatic activation.

### Setting an Override

1. **Right-click** on any conversation in the sidebar
2. Select **Mental Models Override** (🧠 icon)
3. A modal appears showing all enabled models
4. Two options:
   - **Use Default Activation** (checked): Models activate automatically based on context
   - **Custom Override** (unchecked): You manually select which models to use
5. If using custom override:
   - **Check** the models you want active
   - **Uncheck** the models you don't want
6. Click **Save Override**

### Visual Indicator

Conversations with overrides show a **brain emoji (🧠)** in the top-right corner of the conversation item.

### Removing an Override

1. Right-click the conversation
2. Select **Mental Models Override**
3. Check **Use Default Activation**
4. Click **Save Override**

The brain emoji disappears, and the conversation returns to automatic activation.

---

## Default Mental Models

Polly comes with 12 pre-configured mental models:

### Tier 1: Core Philosophy
1. **Infinite Games** - Continuation over completion
2. **Instruments Over Tracks** - Tools over finished products
3. **Constraint as Meaning** - Limitations enable creativity

### Tier 2: Learning & Thinking
4. **Freire's Pedagogy of Liberation** - Critical consciousness through dialogue
5. **Reverse Engineering** - Understanding by deconstructing
6. **Socratic Method** - Learning through questioning

### Tier 3: Systems & Technical
7. **Systems Thinking** - Interconnections and emergence
8. **First Principles** - Reasoning from fundamental truths
9. **Design Thinking** - Human-centered problem solving

### Tier 4: Communication (Future-Ready)
10. **Inbox Zero** - Email as task management (for Phase 20 Mail)
11. **Async-First Communication** - Documentation over meetings (for Phase 20)
12. **Time Blocking** - Calendar as commitment device (for Phase 20 Calendar)

All default models can be edited or disabled, but not deleted.

---

## Technical Details

### Storage Location

Mental models are stored at: `~/.polly/mental_models.yaml`

### Compression

Models are compressed using **PIL (Polly Internal Language)** achieving ~2.3x compression before being injected into the system prompt. This allows more models to fit in context without hitting token limits.

### API Endpoints

For programmatic access:
- `GET /polly/mental-models/list` - List all models
- `GET /polly/mental-models/{id}` - Get specific model
- `POST /polly/mental-models/create` - Create new model
- `PUT /polly/mental-models/{id}` - Update model
- `DELETE /polly/mental-models/{id}` - Delete model
- `POST /polly/mental-models/{id}/toggle` - Toggle enabled/disabled
- `GET /polly/mental-models/active` - Get active models for context

### Override Storage

Per-conversation overrides are stored in localStorage:
```javascript
localStorage['mm_override_<conversation_id>'] = {
  useDefaults: false,
  modelIds: ['infinite_games', 'systems_thinking']
}
```

---

## Best Practices

### 1. Start with Defaults
The 12 default models cover most use cases. Try them first before creating custom ones.

### 2. Be Specific with Activation
The more specific your activation contexts (domains, pages, personas), the more targeted your model will be.

### 3. Keep Principles Concise
3-5 principles per model is ideal. More than that dilutes focus.

### 4. Use Keywords Wisely
Keywords help catch edge cases. Use synonyms and related terms.

### 5. Test with Override
Before enabling a new model globally, test it with per-conversation override on a single chat.

### 6. Disable Unused Models
If a model isn't helping, disable it. Too many active models can dilute the effect.

### 7. Edit, Don't Delete
Instead of deleting a model that's not working, try editing its principles or activation contexts first.

---

## Troubleshooting

### Models Not Activating

**Check:**
1. Is the model **enabled**? (toggle switch should be on)
2. Does the activation context match? (check domains, pages, personas)
3. Are there keywords in your query that should trigger it?

**Try:**
- Use per-conversation override to force the model active
- Check the model's activation tags in settings
- Edit the model to add more activation contexts

### Too Many Models Active

**Solution:**
- Disable models you don't use frequently
- Make activation contexts more specific
- Use per-conversation override to limit models for specific chats

### Model Not Having Effect

**Check:**
1. Is the **prompt injection** clear and actionable?
2. Are the **principles** specific enough?
3. Is the model conflicting with other active models?

**Try:**
- Edit the prompt injection to be more directive
- Add specific examples to principles
- Temporarily disable other models to isolate the issue

### Can't Find a Model

**Solution:**
- Use the search/filter in settings (coming in future update)
- Models are sorted alphabetically by name
- Check if it's disabled (disabled models appear dimmed)

---

## Future Enhancements

Planned improvements for mental models:

- **Search and filter** in settings UI
- **Model categories** for better organization
- **Usage statistics** showing how often models activate
- **Model inheritance** (base models that extend others)
- **Community model marketplace** to share and discover models
- **Model versioning** and change history
- **A/B testing** to compare model effectiveness

---

## Questions?

For issues or feature requests related to mental models:
1. Check `PHASE14_MENTAL_MODELS.md` for technical details
2. See `PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md` for architecture
3. Review test files in `tests/test_mental_models*.py` for examples

Mental Models make Polly truly yours. Enjoy customizing your AI assistant! 🧠✨

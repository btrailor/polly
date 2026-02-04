# Persona API Documentation

**Phase 11c: Agent Personas Framework**

The Persona API allows you to interact with specialized AI personas through Polly's REST API. Currently, the Architect persona is available for creating structured notes through a Plan → Build workflow.

## Requirements

- Router v2 must be enabled (`routing_v2.enabled: true` in config.yaml)
- GitHub token configured (for GitHub Models API)
- Polly server running on port 11436

## Available Endpoints

### 1. List Available Personas

**GET** `/persona/list`

Returns all available personas with their modes and descriptions.

```bash
curl -X GET http://localhost:11436/persona/list
```

**Response:**
```json
{
  "personas": [
    {
      "name": "architect",
      "default_mode": "plan",
      "available_modes": ["plan", "build"],
      "description": "Architect persona for planning and building complex tasks..."
    }
  ]
}
```

---

### 2. Activate a Persona

**POST** `/persona/activate`

Activates a persona and initializes it in its default mode.

```bash
curl -X POST http://localhost:11436/persona/activate \
  -H "Content-Type: application/json" \
  -d '{"persona_name": "architect"}'
```

**Request Body:**
```json
{
  "persona_name": "architect"
}
```

**Response:**
```json
{
  "success": true,
  "state": {
    "persona_name": "architect",
    "current_mode": "plan",
    "data": {},
    "mode_history": [],
    "activated_at": "2026-01-30T07:39:46.113874",
    "last_interaction": "2026-01-30T07:39:46.113874"
  }
}
```

---

### 3. Process User Input with Persona

**POST** `/persona/process`

Processes user input with the active persona in its current mode.

```bash
curl -X POST http://localhost:11436/persona/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Create a note about Python async/await best practices",
    "metadata": {
      "page": "scrolls",
      "domain": "scrolls"
    }
  }'
```

**Request Body:**
```json
{
  "user_message": "Create a note about Python async/await",
  "metadata": {
    "page": "scrolls",
    "domain": "scrolls"
  }
}
```

**Response (Plan Mode):**
```json
{
  "success": true,
  "response": {
    "content": "**Planning Analysis**\n\nYou would like a note...",
    "mode": "plan",
    "actions": [
      {
        "type": "show_questions",
        "data": {
          "questions": [
            "Should the note focus on beginner or advanced concepts?",
            "Do you want code examples included?"
          ],
          "can_skip": false
        }
      }
    ],
    "metadata": {
      "plan": {
        "understanding": "...",
        "questions": [...],
        "outline": [...],
        "needs_clarification": true
      },
      "model_used": "openai/gpt-4o",
      "tokens_in": 295,
      "tokens_out": 415,
      "cost": 0.0048875
    },
    "timestamp": "2026-01-30T07:39:56.261521"
  }
}
```

**Response (Build Mode):**
```json
{
  "success": true,
  "response": {
    "content": "**Generated Content**\n\n# Python Async Best Practices...",
    "mode": "build",
    "actions": [
      {
        "type": "show_preview",
        "data": {
          "content": "# Python Async Best Practices...",
          "title": "Python Async Best Practices",
          "format": "markdown",
          "preview_type": "note"
        }
      }
    ],
    "metadata": {
      "generated_content": {
        "content": "...",
        "format": "markdown",
        "title": "...",
        "generated_at": "2026-01-30T07:40:08.675736"
      },
      "model_used": "openai/gpt-4o",
      "tokens_in": 252,
      "tokens_out": 154,
      "cost": 0.00217
    }
  }
}
```

---

### 4. Switch Persona Mode

**POST** `/persona/switch-mode`

Switches the active persona to a different mode.

```bash
curl -X POST http://localhost:11436/persona/switch-mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "build"}'
```

**Request Body:**
```json
{
  "mode": "build"
}
```

**Response:**
```json
{
  "success": true,
  "state": {
    "persona_name": "architect",
    "current_mode": "build",
    "data": {
      "current_plan": {...}
    },
    "mode_history": [
      {
        "from": "plan",
        "to": "build",
        "timestamp": "2026-01-30T07:40:01.041760"
      }
    ]
  }
}
```

---

### 5. Get Persona State

**GET** `/persona/state`

Returns the current state of the active persona.

```bash
curl -X GET http://localhost:11436/persona/state
```

**Response (Active):**
```json
{
  "active": true,
  "state": {
    "persona_name": "architect",
    "current_mode": "build",
    "data": {...},
    "mode_history": [...],
    "activated_at": "2026-01-30T07:39:46.113874",
    "last_interaction": "2026-01-30T07:40:08.675785"
  }
}
```

**Response (Inactive):**
```json
{
  "active": false,
  "state": null
}
```

---

### 6. Deactivate Persona

**POST** `/persona/deactivate`

Deactivates the current persona and clears its state.

```bash
curl -X POST http://localhost:11436/persona/deactivate
```

**Response:**
```json
{
  "success": true
}
```

---

## Complete Workflow Example

### Architect Persona: Create a Note

**Step 1: Activate Architect**
```bash
curl -X POST http://localhost:11436/persona/activate \
  -H "Content-Type: application/json" \
  -d '{"persona_name": "architect"}'
```

**Step 2: Process in Plan Mode**
```bash
curl -X POST http://localhost:11436/persona/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Create a note about Docker multi-stage builds",
    "metadata": {"page": "scrolls"}
  }'
```

Response includes:
- Understanding of the request
- 2-5 clarifying questions
- Initial outline structure

**Step 3: (Optional) Answer Questions**
```bash
curl -X POST http://localhost:11436/persona/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Focus on practical examples with Python projects. Include common pitfalls.",
    "metadata": {"page": "scrolls"}
  }'
```

**Step 4: Switch to Build Mode**
```bash
curl -X POST http://localhost:11436/persona/switch-mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "build"}'
```

**Step 5: Generate Content**
```bash
curl -X POST http://localhost:11436/persona/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Generate the note",
    "metadata": {"page": "scrolls"}
  }'
```

Response includes:
- Complete markdown content
- Show preview action
- Generation metadata (tokens, cost)

**Step 6: Deactivate**
```bash
curl -X POST http://localhost:11436/persona/deactivate
```

---

## Error Responses

### Router v2 Not Enabled
```json
{
  "detail": "Persona system requires Router v2 (set routing_v2.enabled=true in config)"
}
```

### Persona Not Found
```json
{
  "detail": "Persona 'invalid_name' not found"
}
```

### No Active Persona
```json
{
  "detail": "No active persona"
}
```

### Missing Required Field
```json
{
  "detail": "persona_name is required"
}
```

---

## Action Types

Personas return actions that guide the UI:

### `show_questions`
Display questions to the user in Plan mode.
```json
{
  "type": "show_questions",
  "data": {
    "questions": ["Question 1?", "Question 2?"],
    "can_skip": false
  }
}
```

### `show_preview`
Display generated content in Build mode.
```json
{
  "type": "show_preview",
  "data": {
    "content": "# Markdown content...",
    "title": "Note Title",
    "format": "markdown",
    "preview_type": "note"
  }
}
```

### `suggest_mode_switch`
Suggest switching to a different mode.
```json
{
  "type": "suggest_mode_switch",
  "data": {
    "suggested_mode": "build",
    "reason": "Plan is complete"
  }
}
```

---

## Metadata Fields

### Plan Mode Metadata
```json
{
  "plan": {
    "understanding": "Summary of request",
    "questions": ["Q1", "Q2"],
    "outline": [
      {"level": 1, "title": "Section"},
      {"level": 2, "title": "Subsection"}
    ],
    "template": null,
    "user_answers": {},
    "needs_clarification": true,
    "created_at": "2026-01-30T07:39:56.261462"
  },
  "model_used": "openai/gpt-4o",
  "tokens_in": 295,
  "tokens_out": 415,
  "cost": 0.0048875
}
```

### Build Mode Metadata
```json
{
  "generated_content": {
    "content": "# Full markdown content...",
    "format": "markdown",
    "title": "Note Title",
    "tags": [],
    "metadata": {},
    "generated_at": "2026-01-30T07:40:08.675736"
  },
  "model_used": "openai/gpt-4o",
  "tokens_in": 252,
  "tokens_out": 154,
  "cost": 0.00217
}
```

---

## Cost Information

Persona operations use GitHub Models API (free tier):

- **Plan Mode**: ~$0.005 per request (GPT-4o balanced)
- **Build Mode**: ~$0.002-0.01 per request (GPT-4o thorough)
- **Total Workflow**: ~$0.01-0.02 per complete note

Costs are tracked in metadata for transparency.

---

## Integration Notes

### Frontend Integration
1. Use `/persona/list` to populate persona selector
2. Use `/persona/state` to check if persona is active
3. Use `/persona/process` for all user interactions
4. Parse `actions` array to update UI (show questions, preview, etc.)
5. Track `mode_history` to show workflow progress

### State Management
- Persona state is stored server-side
- State persists across requests until deactivation
- Each request updates `last_interaction` timestamp
- Mode switches are recorded in `mode_history`

### Conversation Context
- All persona interactions are added to `polly.conversation_history`
- This enables context-aware responses across mode switches
- State is reset on deactivation

---

## Future Enhancements (Phase 16c)

- **Intent Detection**: Automatically activate personas based on user query
- **Template System**: Scan user's template folder for structured notes
- **Librarian Persona**: Search and organize existing notes
- **Critic Persona**: Review and improve note quality
- **Teacher Persona**: Socratic questioning for learning

---

## Support

For issues or questions:
- Check `/tmp/polly-server.log` for server logs
- Verify Router v2 is enabled in `config.yaml`
- Ensure GitHub token is configured via secrets_manager
- Test with simple examples before complex workflows

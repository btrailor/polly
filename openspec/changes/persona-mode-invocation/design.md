# Persona Mode Invocation — Design

**Last Updated:** February 2026

---

## Command Registry

**File:** `core/personas/commands.py` (new)

Registry maps command strings to `(persona, mode)`. Each entry has:
- `command` — Primary string (e.g. `learning-path`)
- `persona` — Persona slug
- `mode` — Mode slug (or `None` for default mode)
- `description` — Short text for autocomplete
- `aliases` — Optional list of alternate commands (e.g. `curriculum` → same as `learning-path`)

```python
CommandDef = TypedDict('CommandDef', {
    'command': str,
    'persona': str,
    'mode': Optional[str],
    'description': str,
    'aliases': Optional[List[str]]
})

COMMANDS: List[CommandDef] = [
    {"command": "teach", "persona": "professor", "mode": "socratic", "description": "Guided learning via dialogue"},
    {"command": "learning-path", "persona": "professor", "mode": "curriculum", "description": "Design a structured curriculum"},
    {"command": "curriculum", "persona": "professor", "mode": "curriculum", "description": "Alias for learning-path"},
    {"command": "explain", "persona": "professor", "mode": "explain", "description": "Clear explanation with examples"},
    {"command": "quiz", "persona": "professor", "mode": "quiz", "description": "Test understanding"},
    {"command": "save", "persona": "scribe", "mode": "capture", "description": "Save conversation as KB note"},
    {"command": "note", "persona": "scribe", "mode": "capture", "description": "Alias for save"},
    {"command": "plan", "persona": "architect", "mode": "plan", "description": "Analyze and create plan"},
    {"command": "build", "persona": "architect", "mode": "build", "description": "Execute plan / generate content"},
]
```

**Lookup:** `get_command(cmd: str) -> Optional[Tuple[str, Optional[str]]]` returns `(persona, mode)` or `None`. Resolves aliases via a reverse map built at module load.

---

## API Changes

### POST /persona/process

**Request body extended:**

```json
{
  "user_message": "Create path for Python",
  "persona_name": "professor",
  "persona_mode": "curriculum",
  "metadata": {...}
}
```

- `persona_mode` — Optional. When present, after activating `persona_name`, call `switch_mode(persona_mode)` before processing. Must be a valid mode for that persona.

### GET /persona/commands (new endpoint)

**Response:**

```json
{
  "commands": [
    {
      "command": "learning-path",
      "persona": "professor",
      "mode": "curriculum",
      "description": "Design a structured curriculum"
    },
    ...
  ]
}
```

Frontend uses this for autocomplete. Can optionally merge into `GET /persona/list` response as `commands` field.

---

## Polly Flow

When `process_with_persona` is called with `persona_mode`:

1. `activate_persona(persona_name)` — As today
2. If `persona_mode` provided and valid for persona: `switch_mode(persona_mode)`
3. Process `user_message` with active persona (now in correct mode)

**Polly method signature:** Add optional `persona_mode` to `process_with_persona(user_message, metadata, persona_mode=None)`. Server extracts from request and passes through.

---

## Frontend Flow

### Send Path

Before calling `persona/process` or `polly/query`:

1. **Check for `/` prefix** — If `message.trimStart().startsWith('/')`:
   - Parse command: extract first token after `/` (e.g. `learning-path` or `learning-path Create path for Python`)
   - Look up via registry (or `GET /persona/commands` cached) → `(persona, mode)`
   - If found:
     - `user_message` = rest of message (trimmed), or `"Continue"` if empty
     - `persona_name` = resolved persona
     - `persona_mode` = resolved mode
     - Route to `persona/process` with these params
   - If not found: treat as normal message (or show "Unknown command" inline)

2. **No `/` prefix** — Unchanged: use active persona from dropdown if set, else `polly/query`.

### Autocomplete

- On `keydown` or `input`, when caret is at start and user types `/`:
  - Show dropdown below input with commands from `GET /persona/commands` (or embedded static list for offline)
  - On select: insert `/command ` (with trailing space)
  - On `Escape`: hide
- Filter as user continues typing after `/` (e.g. `/lear` → show `learning-path`)

### Placeholder

Update chat input placeholder to hint at commands, e.g.:
`"Ask anything... or use /teach, /learning-path, /save"`

---

## Extensibility

- **New persona:** Add entries to `COMMANDS` in `commands.py`
- **New mode:** Add command mapping to that mode
- **Aliases:** Add another `CommandDef` with same `persona`/`mode`, or use `aliases` field in lookup

---

## Key Files

| File | Change |
|------|--------|
| `core/personas/commands.py` | **New** — Command registry, `get_command()`, `list_commands()` |
| `core/polly.py` | Extend `process_with_persona` to accept and apply `persona_mode` |
| `interfaces/server.py` | Extend `persona/process` request body; add `GET /persona/commands` |
| `electron-app/src/renderer/app.js` | Command parsing before send; autocomplete UI; sync persona selector when command resolves |
| `electron-app/src/renderer/index.html` | Placeholder text update |

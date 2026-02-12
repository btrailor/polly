# Persona Mode Invocation — Tasks

**Last Updated:** February 2026  
Backend before frontend when both change.

---

## 1. Backend: Command Registry

- [x] Create `core/personas/commands.py`:
  - `CommandDef` TypedDict and `COMMANDS` list (per design)
  - `get_command(cmd: str) -> Optional[Tuple[str, Optional[str]]]` — resolve command/alias to (persona, mode)
  - `list_commands() -> List[Dict]` — for API response

## 2. Backend: Polly process_with_persona

- [x] Extend `process_with_persona(user_message, metadata, persona_mode=None)` in `core/polly.py`
- [ ] After `activate_persona`, if `persona_mode` provided: call `switch_persona_mode(persona_mode)` (or persona_manager.switch_mode)
- [ ] Validate mode is in persona's `available_modes` before switching

## 3. Backend: API

- [x] Extend `POST /persona/process` request body to accept `persona_mode` (optional)
- [ ] Pass `persona_mode` from request to `polly.process_with_persona`
- [ ] Add `GET /persona/commands` returning `{"commands": [...]}` from `list_commands()`

## 4. Frontend: Command Parsing

- [x] Before send, check if message starts with `/`
- [ ] Parse command token and remainder (or fetch/cache commands from API)
- [ ] Resolve command → persona + mode; if found, route to `persona/process` with persona_name, persona_mode, user_message (rest of text)
- [ ] Update persona selector UI to reflect resolved persona when command is used

## 5. Frontend: Autocomplete

- [x] On `/` at start of input, show dropdown with commands + descriptions
- [ ] Filter as user types (e.g. `/lear` → learning-path)
- [ ] On select: insert `/command ` and focus input
- [ ] On Escape: dismiss

## 6. Frontend: Placeholder

- [x] Update chat input placeholder to include command hint, e.g. "Ask anything... or use /teach, /learning-path, /save"

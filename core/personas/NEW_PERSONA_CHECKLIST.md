# New Persona Development Checklist

**Quick Reference** - See full guide in `docs/PERSONA_SYSTEM_ARCHITECTURE.md` → "Developer Guide: Adding New Personas"

## Essential Steps

### 1. Create Persona Class
- [ ] `core/personas/implementations/{name}.py`
- [ ] Inherit from `AgentPersona`
- [ ] Define modes and implement `process()`

### 2. Register Persona
- [ ] Add to `PERSONA_REGISTRY` in `core/personas/manager.py`
- [ ] Update instantiation logic if needs dependencies

### 3. ⚠️ Add Introduction Message (REQUIRED)
- [ ] **Add to `core/pedagogy/coaching_templates.py`**
  ```python
  PERSONA_INTRODUCTIONS: Dict[str, str] = {
      "your_persona": (
          "Hello! I'm {Name}, and I help you {function}. "
          "{Approach description}. "
          "What would you like to {action}?"
      ),
  }
  ```
- [ ] Keep it 2-3 sentences
- [ ] Frame as invitation, not instruction
- [ ] End with open question

### 4. Test Introduction
- [ ] First activation returns introduction
- [ ] Second activation does NOT return introduction
- [ ] `user-journey.json` tracks `persona_intro_{name}`

### 5. Document
- [ ] Update `docs/PERSONA_API.md`
- [ ] Update `docs/PERSONA_SYSTEM_ARCHITECTURE.md`
- [ ] Add changelog entry

## Common Mistakes

❌ **Forgetting introduction message** → Users get no onboarding  
❌ **Not testing first vs repeat activation** → Introduction spam  
❌ **Skipping PERSONA_REGISTRY** → Persona not discoverable  
❌ **Missing dependency injection** → Runtime errors  

## Verification

```bash
# Should show your persona
curl -X GET http://localhost:11436/persona/list

# Should return introduction (first time)
curl -X POST http://localhost:11436/persona/activate \
  -H "Content-Type: application/json" \
  -d '{"persona_name":"your_name"}'

# Should NOT return introduction (second time)
curl -X POST http://localhost:11436/persona/activate \
  -H "Content-Type: application/json" \
  -d '{"persona_name":"your_name"}'

# Check journey tracking
cat ~/.local/share/polly/user-journey.json
```

---

**Full documentation:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` → Developer Guide section

# Constitutional Epistemology — Critical Integration Fix

**Date:** February 15, 2026  
**Issue:** Constitutional layer not actually sent to LLM  
**Status:** ✅ FIXED

---

## Problem Discovered

During testing, we discovered the constitutional layer was implemented but **not actually being sent to the LLM** with queries.

### Why It Wasn't Working

The constitutional layer was added to `PersonaManager.get_system_prompt()`, but this method was not being used when personas made LLM calls. Instead, each persona calls `BasePersona._build_messages()` which uses the persona's own `get_system_prompt()` method — which only returns the persona-specific prompt, not the constitutional layer.

**Flow that was happening:**
```
User query → Persona.process()
           → Persona._build_messages()
           → Persona.get_system_prompt()  ← Only returns persona prompt
           → LLM call (missing constitutional layer!)
```

**PersonaManager.get_system_prompt()** with the constitutional layer was only used for metadata/documentation purposes, not for actual LLM calls.

---

## Solution

Modified `BasePersona._build_messages()` in `core/personas/base.py` to inject the constitutional layer before the persona-specific prompt.

### Changes Made

**File:** `core/personas/base.py`

1. **Added import:**
   ```python
   from core.constitutional import get_constitutional_layer
   ```

2. **Modified `_build_messages()` method:**
   - Changed from single system prompt to multi-part system prompt
   - Always includes constitutional layer as first part
   - Appends persona-specific prompt as second part
   - Joins with separator (`\n\n---\n\n`)

**Before:**
```python
def _build_messages(self, context, system_prompt=None, include_history=True):
    messages = []
    
    if system_prompt is None:
        system_prompt = self.get_system_prompt()
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # ... rest of method
```

**After:**
```python
def _build_messages(self, context, system_prompt=None, include_history=True):
    messages = []
    
    # Build complete system prompt with constitutional layer + persona prompt
    complete_system_prompt_parts = []
    
    # 1. CONSTITUTIONAL LAYER (deepest, always present)
    complete_system_prompt_parts.append(get_constitutional_layer())
    
    # 2. Add persona-specific system prompt
    if system_prompt is None:
        system_prompt = self.get_system_prompt()
    
    if system_prompt:
        complete_system_prompt_parts.append(system_prompt)
    
    # Combine into single system message
    if complete_system_prompt_parts:
        complete_system_prompt = "\n\n---\n\n".join(complete_system_prompt_parts)
        messages.append({"role": "system", "content": complete_system_prompt})
    
    # ... rest of method
```

---

## Impact

This fix ensures that **ALL persona LLM calls** now include the constitutional epistemology layer:

- Default persona ✅
- Architect persona ✅
- Professor persona ✅
- Scribe persona ✅
- Any future personas ✅

The constitutional layer now shapes how Polly thinks about **every query**, regardless of which persona is active.

---

## Testing

**Before fix:** Query "I want to talk about the Somali problem in Minneapolis, MN" would NOT trigger constitutional scapegoat redirect principles.

**After fix:** Same query will now include constitutional layer instructing Polly to:
1. Recognize scapegoat narrative pattern
2. Acknowledge underlying grievance
3. Redirect to structural analysis
4. Surface cui bono questions
5. Never label the user

---

## Verification

```bash
# Verify syntax is valid
python3 -m py_compile /Users/brettgershon/polly/core/personas/base.py

# Verify constitutional layer can be imported
python3 -c "from core.constitutional import get_constitutional_layer; print(len(get_constitutional_layer()))"
# Expected: 2051
```

---

## Related Files

- `core/personas/base.py` — **Modified** (the fix)
- `core/constitutional/layer.py` — Contains the constitutional prompt
- `core/personas/manager.py` — Already had constitutional integration (but wasn't used for LLM calls)
- `openspec/changes/constitutional-epistemology/IMPLEMENTATION_STATUS.md` — Updated with fix details
- `openspec/specs/ethics/spec.md` — Updated to document base.py as critical integration point

---

## Design Principle Maintained

> "The user never gets lectured. They get a better education."

The constitutional layer provides **better analysis**, not content filtering:
- Never refuses topics
- Never labels users
- Never moralizes
- Always leads with curiosity
- Provides deeper structural analysis
- Makes shallow explanations look shallow by offering better ones

---

## Next Steps

1. ✅ Constitutional layer now active in all LLM calls
2. **Test with real queries** — Use `tests/verify_constitutional.py` for testing guide
3. **Monitor responses** — Verify constitutional principles are being applied
4. **Optional manual testing** — Test 13 queries from testing framework

---

**Status:** Constitutional Epistemology is now **fully implemented and active** in Polly.

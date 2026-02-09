# Testing Guide: Context-Aware Persona System

## ✅ Status: Polly is Running

**Backend:** http://localhost:11436 (healthy)  
**Frontend:** Electron app running  
**Syntax:** All JavaScript validated

---

## How to Test

### Step 1: Open DevTools Console

1. In Polly, press **Cmd+Option+I** (Mac) or **Ctrl+Shift+I** (Windows/Linux)
2. Click the **Console** tab
3. Keep this open during testing to see logs

**What to look for:**
- `[Persona Intent] Detected <persona> intent: <query>`
- `[Persona Switch Dialog] Shown for: <persona>`
- `[Persona Switch] Switched to: <persona>`

---

### Step 2: Test Scribe Detection

**Try these queries in the floating chat bar or sidebar:**

#### Should Trigger Scribe 📝

1. **"Make a note"**
   - Expected: Dialog appears suggesting Scribe
   - Console: `[Persona Intent] Detected scribe intent: Make a note`

2. **"Save this conversation"**
   - Expected: Dialog appears suggesting Scribe
   - Console: `[Persona Intent] Detected scribe intent: Save this conversation`

3. **"Take notes on this meeting"**
   - Expected: Dialog appears suggesting Scribe

4. **"Capture this for later"**
   - Expected: Dialog appears suggesting Scribe

5. **"Remember this important detail"**
   - Expected: Dialog appears suggesting Scribe

6. **"Write this down"**
   - Expected: Dialog appears suggesting Scribe

7. **"Log this conversation"**
   - Expected: Dialog appears suggesting Scribe

8. **"Record this discussion"**
   - Expected: Dialog appears suggesting Scribe

9. **"Document our meeting"**
   - Expected: Dialog appears suggesting Scribe

---

### Step 3: Test Architect Detection

**Try these queries:**

#### Should Trigger Architect 📐

1. **"Create a note about Docker"**
   - Expected: Dialog appears suggesting Architect
   - Console: `[Persona Intent] Detected architect intent: Create a note about Docker`

2. **"Generate a document about React hooks"**
   - Expected: Dialog appears suggesting Architect

3. **"Help me write a guide for beginners"**
   - Expected: Dialog appears suggesting Architect

4. **"Draft an article about AI"**
   - Expected: Dialog appears suggesting Architect

5. **"Plan out a tutorial on Python"**
   - Expected: Dialog appears suggesting Architect

6. **"Build a guide for TypeScript"**
   - Expected: Dialog appears suggesting Architect

7. **"Outline a document on project management"**
   - Expected: Dialog appears suggesting Architect

---

### Step 4: Test Dialog Behavior

**When dialog appears:**

#### Visual Checks
- [ ] Dialog has dark background with blur
- [ ] Correct persona icon shows (📝 for Scribe, 📐 for Architect)
- [ ] Persona name is displayed correctly
- [ ] Description text is clear and readable
- [ ] Your query is quoted in gray box at bottom
- [ ] Two buttons: "Keep Current" (gray) and "Switch to [Persona]" (orange)
- [ ] Animation is smooth (slides up, fades in)

#### Interaction Checks
- [ ] Clicking "Switch to [Persona]" closes dialog and activates persona
- [ ] Clicking "Keep Current" closes dialog and proceeds without switch
- [ ] Clicking outside dialog (on overlay) closes without switching
- [ ] Pressing **Escape** key closes without switching
- [ ] Dialog appears on top of everything (z-index: 300)

---

### Step 5: Test Persona Activation

**After clicking "Switch to [Persona]":**

#### Check Persona Dropdown
1. Look at the persona selector in the floating chat controls
2. It should show the activated persona (e.g., "Scribe" or "Architect")

#### Check Mode Selector
1. Mode dropdown should be enabled and populated
2. For Scribe: Shows [Capture, Organize, Enrich, Edit]
3. For Architect: Shows [Plan, Build]

#### Check Console
- [ ] Look for: `[Persona Switch] Switched to: scribe` (or architect)
- [ ] No JavaScript errors
- [ ] Persona activation successful

#### Send the Query
1. After persona activates, your original query should be sent
2. Response should come from the activated persona
3. Check if response differs from default behavior

---

### Step 6: Test Negative Cases (Should NOT Trigger)

**These queries should proceed normally WITHOUT showing dialog:**

1. **"What's the weather today?"**
   - Expected: No dialog, normal query processing

2. **"Tell me a joke"**
   - Expected: No dialog, normal query processing

3. **"How do I install Docker?"**
   - Expected: No dialog, normal query processing

4. **"Explain React hooks to me"**
   - Expected: No dialog, normal query processing

5. **"What is machine learning?"**
   - Expected: No dialog, normal query processing

**Console check:**
- Should NOT see `[Persona Intent] Detected` messages
- Query processes immediately

---

### Step 7: Test Edge Cases

#### Already Using Suggested Persona
1. Manually activate Scribe persona from dropdown
2. Type: "Make a note"
3. Expected: NO dialog (already using Scribe), proceeds directly

#### Multiple Rapid Messages
1. Type "Make a note" and press Enter
2. Immediately type "Create a guide" and press Enter
3. Expected: Each gets its own persona check independently

#### Dialog Open + New Message
1. Type "Make a note" (dialog opens)
2. Type another message in input while dialog is open
3. Expected: Previous dialog should be handled properly

#### Empty Persona (Default)
1. Make sure no persona is selected (dropdown shows "Default")
2. Type "Save this conversation"
3. Expected: Dialog suggests switching to Scribe
4. Confirm switch
5. Verify Scribe activates

---

## Troubleshooting

### Dialog Doesn't Appear

**Check:**
1. Open Console (Cmd+Option+I)
2. Look for errors (red text)
3. Check if intent was detected: Search console for `[Persona Intent]`
4. Verify CSS loaded: Go to Network tab, look for `persona-switch-dialog.css`

**Solution:**
```bash
# Hard refresh (clears cache)
# Press Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)

# Or restart Polly:
cd /Users/brettgershon/polly/electron-app
npm start
```

---

### Persona Doesn't Activate

**Check:**
1. Console for: `[Persona Switch] Error`
2. Backend is running: `curl http://localhost:11436/health`
3. Persona exists: `curl http://localhost:11436/persona/list`

**Solution:**
```bash
# Restart backend
cd /Users/brettgershon/polly
pkill -f "uvicorn.*11436"
python -m uvicorn interfaces.server:app --reload --port 11436
```

---

### Wrong Persona Suggested

**This is expected in some cases!** The patterns are conservative to avoid false positives.

**Report findings:**
- What query did you type?
- What persona was suggested?
- What persona SHOULD have been suggested?
- Console logs

We can adjust patterns based on real usage.

---

### Dialog Appears Too Often

**This might indicate patterns are too broad.**

**Report:**
- What queries trigger unwanted dialogs?
- How frequently does it happen?
- Is it annoying or helpful?

We can make patterns more specific.

---

## Success Criteria

### Minimum Viable Test (Must Pass)

- [x] Polly starts without errors
- [ ] "Make a note" triggers Scribe dialog
- [ ] "Create a note about Docker" triggers Architect dialog
- [ ] Dialog has correct styling and animations
- [ ] "Switch to [Persona]" button activates persona
- [ ] "Keep Current" button proceeds without switch
- [ ] Persona dropdown updates after switch
- [ ] No console errors during any test

---

## Test Results Template

Copy this template and fill it out after testing:

```
=== TEST RESULTS ===

Date: [DATE]
Tester: [YOUR NAME]

SCRIBE TESTS:
[ ] "Make a note" - Works / Fails / Issue: _____
[ ] "Save this conversation" - Works / Fails / Issue: _____
[ ] "Take notes" - Works / Fails / Issue: _____

ARCHITECT TESTS:
[ ] "Create a note about Docker" - Works / Fails / Issue: _____
[ ] "Generate a document" - Works / Fails / Issue: _____
[ ] "Help me write a guide" - Works / Fails / Issue: _____

DIALOG BEHAVIOR:
[ ] Visual styling - Good / Issues: _____
[ ] Animations - Smooth / Laggy / Broken
[ ] Button interactions - All work / Issues: _____
[ ] Keyboard shortcuts - Work / Don't work

PERSONA ACTIVATION:
[ ] Dropdown updates - Yes / No
[ ] Mode selector populates - Yes / No
[ ] Query processes through persona - Yes / No

NEGATIVE CASES:
[ ] "What's the weather" - No dialog / Dialog appeared (bug)
[ ] "Tell me a joke" - No dialog / Dialog appeared (bug)

EDGE CASES:
[ ] Already using persona - No dialog / Dialog appeared (bug)
[ ] Multiple rapid messages - Handled / Issues: _____

CONSOLE ERRORS:
[ ] No errors / Errors found: _____

OVERALL ASSESSMENT:
[ ] Ready for production
[ ] Needs minor fixes: _____
[ ] Needs major fixes: _____

ADDITIONAL NOTES:
_______________________
```

---

## Next Steps After Testing

1. **If tests pass:** System is ready! Start using it in daily workflow.

2. **If minor issues:** Report findings, we'll adjust patterns or fix bugs.

3. **If major issues:** We'll debug together.

4. **Gather real usage data:** After a few days, review:
   - Which patterns trigger most often?
   - Are there false positives (wrong suggestions)?
   - Are there false negatives (missed opportunities)?
   - User feedback on annoyance vs. helpfulness

---

## Quick Test Commands

**Check backend:**
```bash
curl http://localhost:11436/health
```

**List personas:**
```bash
curl http://localhost:11436/persona/list
```

**Check Polly is running:**
```bash
ps aux | grep -i "electron.*polly" | grep -v grep
```

**Restart Polly:**
```bash
pkill -f "electron.*polly"
cd /Users/brettgershon/polly/electron-app
npm start
```

**View console logs:**
Open DevTools in Polly (Cmd+Option+I), click Console tab

---

## Ready to Test! 🚀

Polly is running and waiting for you. Start with the simple tests:

1. Type: **"Make a note"**
2. Watch for the dialog
3. Click "Switch to Scribe"
4. Verify Scribe activates

Then work through the rest of the test cases. Good luck!

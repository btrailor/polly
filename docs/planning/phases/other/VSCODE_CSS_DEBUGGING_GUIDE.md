# VSCode CSS Import Map Debugging Guide

**Date:** February 5, 2025  
**Status:** Active Debugging

---

## Problem

CSS files are being loaded as JavaScript modules, causing MIME type errors:
```
Failed to load module script: Expected a JavaScript-or-Wasm module script but the server responded with a MIME type of "text/css"
```

## How CSS Import Maps Work in VSCode

1. **CSS Development Service** finds all CSS files in `src/vs/` directory
2. **Import Map Creation** maps CSS file URLs to blob URLs containing JavaScript
3. **Blob URLs** contain code that calls `_VSCODE_CSS_LOAD(url)` to load CSS via `<link>` tag
4. **Browser** intercepts CSS imports using the import map before trying to load CSS directly

## Current Instrumentation

### Logging Points Added

1. **CSS Module Discovery** (`cssDevService.ts`)
   - Logs when CSS files are found
   - Logs path calculation
   - Logs fallback usage

2. **Import Map Setup** (`workbench.ts`)
   - Logs when `setupCSSImportMaps` is called
   - Logs CSS module count
   - Logs base URL

3. **Import Map Entry Creation** (`workbench.ts`)
   - Logs each import map entry created
   - Logs CSS URL and blob URL

4. **Import Map DOM Addition** (`workbench.ts`)
   - Logs when import map is added to DOM
   - Verifies import map is accessible

5. **Module Loading** (`workbench.ts`)
   - Logs before workbench module import
   - Checks if import map exists

## Debugging Steps

### Step 1: Verify CSS Modules Are Found

**Check logs for:**
- `CSS module computation` - Should show CSS files being found
- `CSS files found via fallback` - Should show count and sample paths

**Expected:** 299+ CSS files found

### Step 2: Verify Import Map Creation

**Check logs for:**
- `setupCSSImportMaps called` - Should show CSS module count > 0
- `Creating import map entries` - Should show base URL and first CSS module
- `Import map entry created` - Should show CSS URL and blob URL for each entry

**Expected:** Import map entries created for all CSS modules

### Step 3: Verify Import Map in DOM

**Check logs for:**
- `Import map added to DOM` - Should show entry count matches CSS modules

**Also check in browser DevTools:**
- Elements tab → Look for `<script type="importmap">`
- Verify import map JSON structure
- Check if entries match CSS file URLs

### Step 4: Verify Module Loading Order

**Check logs for:**
- `About to import workbench module` - Should show import map exists
- Timing: Import map should be added BEFORE module import

**Expected:** Import map exists when modules start loading

### Step 5: Check Browser Network Tab

**In DevTools Network tab:**
- Filter by CSS files
- Check which CSS files are being requested
- Check request URLs vs import map entries
- Check response MIME types

**Expected:** CSS files should be loaded via blob URLs (not direct requests)

---

## Common Issues and Fixes

### Issue 1: CSS Modules Not Found

**Symptom:** `cssModulesCount: 0` in logs

**Fix:**
- Check `CSSDevelopmentService` is enabled (`isEnabled: true`)
- Check `basePath` calculation (should point to `src/` not `out/`)
- Verify CSS files exist in `src/vs/` directory

### Issue 2: Import Map Not Matching

**Symptom:** CSS files still requested directly (Network tab shows CSS file requests)

**Fix:**
- Verify import map entries use absolute URLs
- Check if CSS import paths in JS match import map entries
- Verify base URL calculation is correct

### Issue 3: Import Map Added Too Late

**Symptom:** Modules load before import map is ready

**Fix:**
- Ensure `setupCSSImportMaps` is called before `import(workbenchUrl)`
- Add await to ensure import map is fully set up

### Issue 4: Blob URLs Not Working

**Symptom:** Blob URLs created but CSS not loading

**Fix:**
- Verify `_VSCODE_CSS_LOAD` function is defined
- Check if blob URLs are accessible
- Verify CSP allows blob URLs

---

## Testing Checklist

- [ ] CSS modules are found (299+ files)
- [ ] Import map is created with correct entries
- [ ] Import map is added to DOM before modules load
- [ ] Import map entries match CSS import paths
- [ ] Blob URLs are created correctly
- [ ] `_VSCODE_CSS_LOAD` function is defined
- [ ] No direct CSS file requests in Network tab
- [ ] CSS loads via blob URLs
- [ ] No MIME type errors in console

---

**Last Updated:** February 5, 2025

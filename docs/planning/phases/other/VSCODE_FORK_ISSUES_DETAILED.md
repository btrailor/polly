# VSCode Fork - Detailed Issues Analysis

**Date:** February 5, 2025  
**Purpose:** Document specific issues encountered with VSCode fork to inform Void editor evaluation

---

## Build System Complexity

### Multiple Output Directories

**Issue:** VSCode uses three separate output directories with different purposes:
- `out/` - Client-side compiled code (used by `compile-client`)
- `out-build/` - Build-time compiled code (used by `compile-build-without-mangling`)
- `out-vscode/` - Bundled code (used by `bundle-vscode`)

**Problems:**
- `main.js` is generated in `out-build/` but `package.json` expects it in `out/`
- Required custom gulp task to copy files between directories
- Confusing which directory contains what
- Build tasks must run in specific order

**Example:**
```typescript
// Had to add custom task to copy main.js
const copyMainJsTask = task.define('copy-main-js', () => {
  const source = path.join(root, 'out-build', 'main.js');
  const dest = path.join(root, 'out', 'main.js');
  fs.copyFileSync(source, dest);
});
```

### Complex Gulp Task Dependencies

**Issue:** Build tasks have intricate dependencies:
- `compile-client` depends on `compile-build-without-mangling`
- `bundle-vscode` depends on `compile-build-without-mangling`
- `compile-build-without-mangling` clears `out-build` directory
- Tasks must be run in specific sequence

**Build Time:**
- Full compile: 5-10 minutes
- Incremental: Still requires full `compile-build-without-mangling` for `main.js`

### CSS Bundling Issues

**Development Mode (`VSCODE_DEV=1`):**
- Uses CSS import maps to load individual CSS files
- Requires `CSSDevelopmentService` to find all CSS files using `ripgrep`
- `ripgrep` binary path resolution issues
- Fallback to Node.js file walker needed
- CSS files loaded as JavaScript modules (MIME type errors)

**Production Mode:**
- CSS bundled into `workbench.desktop.main.css`
- esbuild configuration needed to handle CSS
- CSS import statements must be stubbed/removed
- Multiple build configurations for dev vs prod

**Problems Encountered:**
1. CSS files being loaded as JS modules
2. `ripgrep` binary not found
3. `child_process` being bundled into renderer (not allowed)
4. CSS import maps not working correctly

---

## Native Module Issues

### Required Native Modules

1. **`@vscode/policy-watcher`**
   - Failed to compile initially
   - Required workaround to make optional
   - Native binary compilation issues

2. **`@parcel/watcher`**
   - Missing prebuilt binaries
   - Required manual installation: `npm install @parcel/watcher-darwin-arm64 --legacy-peer-deps`
   - Dependency of other modules

3. **`@vscode/ripgrep`**
   - Binary path resolution issues
   - Required fallback mechanism
   - Used by `CSSDevelopmentService`

### Solutions Applied

```typescript
// Made policy watcher optional
try {
  const { createWatcher } = await import('@vscode/policy-watcher');
  // ... use watcher
} catch (err) {
  this.logService.warn('Policy watcher unavailable, continuing without it');
}

// Added ripgrep fallback
if (!fs.existsSync(rg.rgPath)) {
  // Use Node.js file walker instead
  const result = this.findCssFilesRecursive(basePath);
}
```

---

## Codebase Size and Complexity

### Statistics
- **Total Lines:** ~160,000 lines of code
- **TypeScript Files:** Thousands of `.ts` files
- **Build Configuration:** Multiple gulpfiles, complex task system
- **Dependencies:** Hundreds of npm packages

### Modification Challenges
- Large codebase makes finding integration points difficult
- Many files to review for customization
- Risk of breaking existing functionality
- Extensive testing required

---

## Development Workflow Issues

### CSS Development
- Cannot make CSS changes without full rebuild in production mode
- Development mode has CSS import map issues
- Need to disable/enable CSS import maps based on mode
- Complex CSS bundling configuration

### Build Iteration
- Full rebuild required for many changes
- Long build times slow development
- Multiple build steps increase chance of errors
- Difficult to debug build issues

### Hot Reload
- Limited hot reload capabilities
- CSS changes require page refresh
- TypeScript changes require rebuild

---

## Maintenance Burden

### Upstream Tracking
- VSCode releases monthly
- Must track and merge upstream changes
- Merge conflicts common in UI/workbench code
- Requires dedicated developer time (20-30%)

### Documentation Requirements
- All core modifications must be documented
- Integration points must be clearly marked
- Build process must be documented
- Migration path for updates must be planned

### Testing Requirements
- Extensive testing after each merge
- Must verify all Polly features still work
- Must ensure no regressions in VSCode features
- Automated testing helps but manual testing still needed

---

## Specific Technical Issues

### Issue 1: main.js Location Mismatch
**Problem:** `main.js` generated in `out-build/` but expected in `out/`
**Solution:** Added custom gulp task to copy file
**Impact:** Build complexity increased

### Issue 2: Native Module Compilation
**Problem:** `@vscode/policy-watcher` failed to compile
**Solution:** Made watcher optional with try-catch
**Impact:** Feature degradation (policies not updated dynamically)

### Issue 3: CSS Import Maps
**Problem:** CSS files loaded as JavaScript modules
**Solution:** Conditional CSS import map setup based on `VSCODE_DEV`
**Impact:** Complex development/production split

### Issue 4: child_process in Renderer
**Problem:** Node.js built-in modules bundled into renderer
**Solution:** Added to esbuild `external` array
**Impact:** Build configuration complexity

### Issue 5: ripgrep Binary Path
**Problem:** `ripgrep` binary not found
**Solution:** Implemented Node.js fallback file walker
**Impact:** Performance degradation (slower CSS file discovery)

---

## Build Configuration Complexity

### esbuild Configuration
```typescript
// Multiple configurations needed
loader: {
  '.css': 'css', // Bundle CSS
  '.ttf': 'file',
  '.svg': 'file',
  // ...
},
external: [
  'child_process', 'fs', 'path', // Node.js built-ins
  // ... many more
],
plugins: [
  contentsMapper,
  externalOverride,
  removeCSSImports, // Custom plugin to stub CSS imports
]
```

### TypeScript Configuration
- Multiple `tsconfig.json` files
- Different output directories for different purposes
- Complex path mappings
- Source map configuration

### Gulp Tasks
- Dozens of tasks with complex dependencies
- Task serialization and parallelization
- Multiple gulpfiles for different purposes
- Task composition and reuse

---

## Summary of Pain Points

1. **Build Time:** 5-10 minutes is too long for iteration
2. **Build Complexity:** Multiple output directories, complex task dependencies
3. **Native Modules:** Compilation issues, missing binaries
4. **CSS Handling:** Complex dev/prod split, import map issues
5. **Codebase Size:** Large codebase makes modifications difficult
6. **Maintenance:** Monthly merges, frequent conflicts
7. **Development Workflow:** Limited hot reload, full rebuilds needed

---

## What We're Looking For in Void

Based on these issues, Void should ideally have:

1. **Simpler Build System:**
   - Single output directory or clear separation
   - Faster build times (< 2 minutes)
   - Simple build configuration

2. **Fewer Native Dependencies:**
   - Minimal native modules
   - Prebuilt binaries available
   - Or no native modules at all

3. **Better CSS Handling:**
   - Simple CSS bundling
   - No complex dev/prod split
   - Fast CSS iteration

4. **Smaller Codebase:**
   - Easier to understand and modify
   - Clearer architecture
   - Less maintenance burden

5. **Better Development Workflow:**
   - Hot reload for CSS and TypeScript
   - Fast incremental builds
   - Simple development setup

---

**Last Updated:** February 5, 2025

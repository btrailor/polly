# VSCode Work Salvage Plan for Void Migration

**Date:** February 5, 2025  
**Status:** Phase 2 - Complete

---

## Overview

This document outlines how to salvage and apply our VSCode fork work to a Void migration.

---

## Reusable Knowledge and Solutions

### 1. Build System Understanding

**What We Learned:**
- Multiple output directories and their purposes
- Gulp task dependencies and ordering
- Build time optimization strategies
- Development vs. production build differences

**How to Apply to Void:**
- Same build system, so knowledge transfers directly
- Can anticipate similar issues
- Can apply same debugging techniques

**Value:** High - Saves debugging time

---

### 2. CSS Handling Solutions

**What We Developed:**
- CSS import map debugging techniques
- Fallback mechanisms for `ripgrep`
- Node.js built-in module externalization
- CSS development service fixes

**Specific Fixes:**
1. **CSSDevelopmentService fallback**
   ```typescript
   // If ripgrep not found, use Node.js file walker
   if (!fs.existsSync(rg.rgPath)) {
     const result = this.findCssFilesRecursive(basePath);
     resolve(result);
   }
   ```

2. **Node.js module externalization**
   ```typescript
   // In esbuild config
   external: ['child_process', 'fs', 'path', ...]
   ```

3. **CSS import map timing**
   ```typescript
   // Ensure import map added before modules load
   await setupCSSImportMaps(configuration, baseUrl);
   await import(workbenchUrl);
   ```

**How to Apply to Void:**
- Void likely has same CSS system
- Can apply fixes directly
- May need minor adjustments

**Value:** High - Solves known issues immediately

---

### 3. Native Module Handling

**What We Developed:**
- Optional module patterns
- Fallback mechanisms
- Error recovery strategies

**Specific Solutions:**
1. **Policy watcher optional**
   ```typescript
   try {
     const { createWatcher } = await import('@vscode/policy-watcher');
   } catch (err) {
     // Continue without it
   }
   ```

2. **Parcel watcher prebuilt binaries**
   ```bash
   npm install @parcel/watcher-darwin-arm64 --legacy-peer-deps
   ```

**How to Apply to Void:**
- Same native modules likely
- Can apply same patterns
- May need platform-specific adjustments

**Value:** Medium - Prevents known issues

---

### 4. Build Task Optimizations

**What We Developed:**
- Main.js copy task
- Task dependency management
- Build process documentation

**Specific Solutions:**
1. **Copy main.js task**
   ```typescript
   const copyMainJsTask = task.define('copy-main-js', () => {
     const source = path.join(root, 'out-build', 'main.js');
     const dest = path.join(root, 'out', 'main.js');
     fs.copyFileSync(source, dest);
   });
   ```

2. **Task dependencies**
   ```typescript
   const compileClientTask = task.define('compile-client', 
     task.series(
       compileBuildWithoutManglingTask,
       copyMainJsTask
     )
   );
   ```

**How to Apply to Void:**
- Check if Void has same issue
- Apply if needed
- Document differences

**Value:** Medium - May not be needed

---

## Code to Rebuild

### 1. Polly Integration Code

**What Needs Rebuilding:**
- Polly contribution registration
- Backend integration
- API client setup
- Status bar contributions

**Why:**
- Polly-specific code
- Needs to integrate with Void's structure
- May have different extension points

**Effort:** 1-2 weeks

---

### 2. Custom Features

**What Needs Rebuilding:**
- Polly-specific UI components
- Custom routing (if different from Void)
- Persona system integration
- RAG integration hooks

**Why:**
- Polly-specific features
- May need different integration approach
- Void may have different APIs

**Effort:** 1-2 weeks

---

## Migration Checklist

### Phase 1: Setup (Days 1-2)

- [ ] Fork Void repository
- [ ] Set up build environment
- [ ] Run initial build
- [ ] Document any build issues
- [ ] Apply CSS fixes (if needed)
- [ ] Apply native module fixes (if needed)
- [ ] Verify build works

### Phase 2: Integration (Days 3-10)

- [ ] Review Void's model integration
- [ ] Review Void's chat sidebar
- [ ] Plan Polly integration points
- [ ] Integrate Polly backend
- [ ] Customize chat sidebar
- [ ] Add Polly-specific features
- [ ] Test integration

### Phase 3: Polish (Days 11-14)

- [ ] Test all features
- [ ] Fix integration issues
- [ ] Polish UI
- [ ] Documentation
- [ ] Performance optimization

---

## Risk Mitigation

### Build Issues

**Risk:** Void may have different build setup
**Mitigation:** 
- Apply our fixes incrementally
- Test after each fix
- Document differences

### Integration Complexity

**Risk:** Void's APIs may differ
**Mitigation:**
- Review Void's codebase first
- Plan integration carefully
- Build incrementally

### Maintenance Concerns

**Risk:** No upstream updates
**Mitigation:**
- Fork and maintain ourselves
- Document all changes
- Create update process

---

## Time Savings Summary

### From VSCode Work

- **Build knowledge:** 1-2 weeks saved
- **CSS fixes:** 3-5 days saved
- **Native module fixes:** 2-3 days saved
- **Total:** ~2-3 weeks saved

### From Void Features

- **Model integration:** 2-4 weeks saved
- **Chat sidebar:** 2-3 weeks saved
- **Total:** ~4-7 weeks saved

### Net Savings

- **Total potential:** 6-10 weeks
- **Migration effort:** 2-3 weeks
- **Net savings:** 3-7 weeks

---

## Conclusion

**Salvage Value:** ✅ **HIGH**

Our VSCode work provides:
1. Build system knowledge
2. Proven fixes for common issues
3. Debugging techniques
4. Optimization strategies

**Recommendation:** Proceed with migration, applying our fixes incrementally.

---

**Last Updated:** February 5, 2025

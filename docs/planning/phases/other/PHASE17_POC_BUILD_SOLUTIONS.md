# Phase 17 POC: Build Solutions

**Issue:** Native module `@parcel/watcher` fails to compile due to C++ header issues

---

## Problem Analysis

**Root Cause:**
- Command Line Tools only (not full Xcode)
- C++ standard library headers (`<unordered_set>`) not found by node-gyp
- macOS 25.2.0 (very new) may have compatibility issues

**Impact:**
- Full build cannot complete
- File watcher won't work
- **But:** TypeScript compilation might still work

---

## Solution Options

### Option 1: Install Full Xcode (Recommended for POC)

**Pros:**
- ✅ Complete C++ toolchain
- ✅ All headers in expected locations
- ✅ Most reliable solution

**Cons:**
- ❌ Large download (~10GB+)
- ❌ Takes time to install

**Steps:**
```bash
# 1. Install Xcode from App Store
# 2. Set developer directory:
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# 3. Accept license:
sudo xcodebuild -license accept

# 4. Retry build:
cd ~/projects/polly-code
rm -rf node_modules
npm install
npm run compile
```

---

### Option 2: Use VSCode Dev Container

**Pros:**
- ✅ Pre-configured build environment
- ✅ All tools included
- ✅ Isolated from host system

**Cons:**
- ❌ Requires Docker
- ❌ May be slower than native

**Steps:**
```bash
# 1. Install Docker Desktop
# 2. Open in VS Code with Dev Containers extension
# 3. Reopen in container
# 4. Build should work automatically
```

---

### Option 3: Skip Native Modules (Workaround)

**Pros:**
- ✅ Can proceed immediately
- ✅ TypeScript compilation might work

**Cons:**
- ❌ File watcher won't work
- ❌ Some features may be limited
- ❌ Not ideal for full POC validation

**Steps:**
```bash
cd ~/projects/polly-code
npm install --ignore-scripts
# Try to compile TypeScript only
npm run compile
```

---

### Option 4: Fix C++ Headers Manually

**Pros:**
- ✅ No need for full Xcode
- ✅ Keeps current setup

**Cons:**
- ❌ Complex configuration
- ❌ May not work on macOS 25.2.0

**Attempted:**
- Setting SDKROOT
- Setting CXXFLAGS
- Configuring node-gyp

**Status:** Not successful yet

---

## Recommendation

**For POC Completion:**

1. **Short term:** Try Option 3 (skip native modules) to at least get TypeScript compilation working
   - We can study architecture
   - We can write code changes
   - We can test UI changes (if TypeScript compiles)

2. **For full validation:** Install full Xcode (Option 1)
   - Needed to test complete integration
   - Needed for file watcher functionality
   - Most reliable path forward

---

## Current Status

**What Works:**
- ✅ Dependencies installed (with --ignore-scripts)
- ✅ Source code readable
- ✅ Architecture study possible

**What Doesn't Work:**
- ❌ Native module compilation
- ❌ Full build
- ❌ File watcher

**Next Step:**
- Try TypeScript compilation without native modules
- If that works, proceed with architecture study and code changes
- Plan to install Xcode for full POC validation

---

## Testing TypeScript Compilation

Let's see if we can at least compile TypeScript:

```bash
cd ~/projects/polly-code
# Try to compile just TypeScript
npm run compile
```

If this works, we can:
- ✅ Make code changes
- ✅ Compile TypeScript
- ✅ Test UI modifications
- ⚠️ File watcher won't work (but we can work around this)

---

**Decision Point:** Proceed with TypeScript-only compilation, or install full Xcode now?

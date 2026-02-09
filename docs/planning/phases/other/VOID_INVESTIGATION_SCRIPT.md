# Void Editor Investigation Script

**Purpose:** Systematic investigation of Void's features

---

## Step 1: Clone and Explore Repository

```bash
# Clone Void repository
cd /tmp
git clone https://github.com/voideditor/void.git
cd void

# Check repository structure
ls -la
cat README.md
cat VOID_CODEBASE_GUIDE.md 2>/dev/null || echo "No codebase guide found"
```

---

## Step 2: Search for Model Integration

```bash
# Search for AI/model-related code
grep -r "model" --include="*.ts" --include="*.js" src/ | head -20
grep -r "provider" --include="*.ts" --include="*.js" src/ | head -20
grep -r "openai\|anthropic\|claude\|gpt" --include="*.ts" --include="*.js" src/ | head -20
grep -r "AI\|artificial" --include="*.ts" --include="*.js" src/ | head -20
```

---

## Step 3: Search for Chat Sidebar

```bash
# Search for chat-related code
grep -r "chat" --include="*.ts" --include="*.js" src/ | head -20
grep -r "sidebar" --include="*.ts" --include="*.js" src/ | head -20
grep -r "message" --include="*.ts" --include="*.js" src/ | head -20
```

---

## Step 4: Review Key Files

```bash
# Find main entry points
find src -name "*chat*" -o -name "*ai*" -o -name "*model*" | head -20

# Review package.json for dependencies
cat package.json | grep -A 5 -B 5 "dependencies"

# Check for extension or feature documentation
find . -name "*.md" | xargs grep -l "chat\|AI\|model" | head -10
```

---

## Step 5: Build and Test

```bash
# Try to build Void
npm install
npm run compile 2>&1 | head -50

# Check if build succeeds
# Note any errors or issues
```

---

## Expected Findings

### Model Integration
- Provider adapter files
- Routing logic
- Configuration system
- API endpoints

### Chat Sidebar
- UI component files
- Message handling
- Context integration
- Panel/container structure

---

**Note:** This script should be run to gather concrete evidence about Void's features.

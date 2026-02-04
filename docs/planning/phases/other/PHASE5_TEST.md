# Phase 5 Quick Test Guide

## What We Built

Backend integration framework that makes GitHub actually work:
- Fetches your repositories and READMEs
- Indexes them into Polly's RAG system
- Allows natural language queries about your code

## Quick Test (5 minutes)

### 1. Restart Polly

The backend server needs to pick up the new integration code:

```bash
# Stop the app if running
# Then restart:
cd electron-app
npm run dev
```

### 2. Verify GitHub Connection

1. Go to **Settings → Integrations**
2. GitHub should show **green dot** and "connected as @yourusername"
3. If not green, click "connect" again

### 3. Sync Your Repos

1. Click **"sync now"** button on GitHub card
2. Wait 15-30 seconds (fetching repos + READMEs)
3. Should see alert: "Synced X items from GitHub. Indexed X documents."

### 4. Query Your Data

Go to the **Chat** tab and try:

**Simple queries**:
- "what repositories do I have?"
- "list my github projects"
- "show my most recent repos"

**Language-specific**:
- "show me my python projects"
- "what javascript repos do I have?"
- "any typescript projects?"

**Content search**:
- "which repo has docker setup?"
- "do I have any AI or ML projects?"
- "repos about web development"

**Specific lookups**:
- "tell me about the [repo_name] repository"
- "what does [repo_name] do?"

## Expected Results

### Successful Sync

```
Alert: "Synced 30 items from GitHub. Indexed 30 documents."
```

Card should show:
- Green status dot
- "connected as @yourusername"
- "sync now" button active

### Successful Query

Example query: "what python repos do I have?"

Expected response:
```
Based on your GitHub repositories, you have several Python projects:

1. **polly** - Edge-native personal AI assistant
   - Uses Python with FastAPI backend
   - Machine learning and RAG capabilities
   - [link to repo]

2. **[other_repo]** - Description from README
   - Key technologies mentioned
   - [link to repo]

[More repos...]
```

## Troubleshooting

### Sync button does nothing

**Check**:
1. Is Polly server running? (green dot in titlebar)
2. Check DevTools Console (View → Developer → Developer Tools)
3. Look for errors

**Common issue**: Server not restarted after adding integration code
**Solution**: Quit app completely, restart

### "Integration not found" error

**Cause**: Backend hasn't loaded integration module
**Solution**:
1. Check server logs in terminal
2. Restart server
3. Verify `/integrations/` directory exists

### Queries don't return GitHub data

**Check**:
1. Did sync complete successfully?
2. Try more specific query: "list my github repositories"
3. Check if data was indexed (see below)

### Verify Data Was Indexed

Open DevTools Console and run:

```javascript
// Check sync status
fetch('http://localhost:11436/polly/integrations')
  .then(r => r.json())
  .then(console.log)

// Should show:
// {
//   integrations: { github: { status: "connected", ... } },
//   connected: ["github"]
// }
```

## What's Happening Behind the Scenes

```
1. You click "sync now"
   ↓
2. Frontend calls window.polly.integrationSync('github', {...})
   ↓
3. Main process sends HTTP POST to /polly/integrations/sync
   ↓
4. FastAPI receives request with your token
   ↓
5. GitHub integration fetches repos via GitHub API
   ↓
6. For each repo, fetches README (if exists)
   ↓
7. Formats all data into documents
   ↓
8. Adds documents to ChromaDB collection "integration_github"
   ↓
9. Returns: {success: true, fetched: 30, indexed: 30}
   ↓
10. Frontend shows success alert
```

## Sample Data Structure

When you sync, each repo becomes a document like:

```
Content:
"Repository: brettgershon/polly
Description: Edge-native personal AI assistant
Language: Python
Stars: 5, Forks: 2
Topics: ai, machine-learning, electron

--- README ---
# Polly
Personal AI assistant that runs entirely on your edge...
[full README content]"

Metadata:
{
  source: "github",
  type: "repository",
  name: "brettgershon/polly",
  url: "https://github.com/brettgershon/polly",
  language: "Python",
  updated_at: "2024-01-19T...",
  private: false
}
```

This rich content lets Polly answer detailed questions about your projects.

## Advanced: Manual Backend Test

If you want to test the backend directly:

```bash
# In a terminal
cd /Users/brettgershon/polly

# Test integration endpoint
curl -X GET http://localhost:11436/polly/integrations | jq

# Should return:
# {
#   "integrations": {
#     "github": {
#       "name": "github",
#       "status": "connected",
#       ...
#     }
#   },
#   "connected": ["github"]
# }
```

## Success Checklist

- [ ] App restarted and server running
- [ ] GitHub shows green dot
- [ ] "sync now" completes without errors
- [ ] Alert shows "Synced X items"
- [ ] Query "what repos do I have?" returns results
- [ ] Query includes README content
- [ ] Specific queries work (e.g., "python projects")

## If Everything Works

**Congratulations!** You now have a working integration framework. You can:

1. **Search your code** naturally
2. **Find projects** by language, topic, or content
3. **Get context** about repositories
4. **Ask questions** about your codebase

Next up: Phase 6 - Context7 integration for library docs!

## If Something Breaks

Check these in order:

1. **Server logs** in terminal (where you ran `npm run dev`)
2. **DevTools Console** (View → Developer → Developer Tools)
3. **Network tab** in DevTools (check API responses)
4. **Python syntax** - Did all `.py` files compile?

Common fixes:
- Restart app completely
- Check GitHub token still valid (try re-connecting)
- Verify `aiohttp` installed: `./venv/bin/pip list | grep aiohttp`
- Check `/integrations/` directory exists with all 3 files

---

**Ready?** Restart the app and click "sync now"!

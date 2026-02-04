# Phase 6: Enhanced GitHub Integration

**Status:** Not Started  
**Priority:** Low (Optional Enhancement)  
**Estimated Effort:** 3-5 days  
**Dependencies:** Phase 5 (Backend Integration Framework) - Complete ✅

---

## Overview

Enhance the existing GitHub integration with performance improvements, incremental sync, code search, and commit history indexing.

### Current State

**What Works:**
- ✅ GitHub OAuth authentication
- ✅ Repository fetching (up to 30 repos)
- ✅ README content extraction
- ✅ RAG indexing of repos
- ✅ 17 repos currently synced

**Location:** `/integrations/github.py` (390 lines)

### What's Missing

- Incremental sync (currently fetches all repos every time)
- Parallel README fetching (currently sequential, slow)
- Code search within repositories
- Commit history and messages
- Branch and tag information
- Issue/PR content (currently optional, needs improvement)

---

## Goals

### Primary Goals

1. **Incremental Sync**
   - Only fetch repos updated since last sync
   - Use GitHub's `If-Modified-Since` headers
   - Reduce sync time from 30s to ~5s for unchanged repos

2. **Parallel README Fetching**
   - Fetch READMEs concurrently using `asyncio.gather()`
   - 10x speed improvement (30 repos: 30s → 3s)

3. **Code Search**
   - Search file contents within repos
   - Index Python, JavaScript, Rust, Go files
   - Support regex patterns

4. **Commit History**
   - Index recent commits (last 50 per repo)
   - Store commit messages, authors, dates
   - Make commit messages searchable

### Secondary Goals

- Branch and tag information
- Better issue/PR indexing
- Repository activity metrics
- Contributor information

---

## Implementation Plan

### Day 1: Incremental Sync

**Tasks:**
1. Add `last_sync` timestamp to integration state
2. Use GitHub API's `since` parameter
3. Check `updated_at` field for each repo
4. Only re-fetch changed repos
5. Test with 30 repos (verify only changed repos fetched)

**Deliverables:**
- Updated `/integrations/github.py` (+50 lines)
- State persistence for sync timestamps

**API Change:**
```python
async def fetch_repos(self, since: Optional[datetime] = None):
    """Fetch repos, optionally filtering by update time."""
    params = {"per_page": 30}
    if since:
        params["since"] = since.isoformat()
    # ... existing code
```

### Day 2: Parallel README Fetching

**Tasks:**
1. Convert `fetch_readme()` to async
2. Use `asyncio.gather()` to fetch all READMEs in parallel
3. Add rate limit handling (GitHub: 5000 req/hour)
4. Add retry logic with exponential backoff
5. Benchmark: measure speed improvement

**Deliverables:**
- Parallel fetching implementation (+80 lines)
- Performance benchmarks

**Code Example:**
```python
async def fetch_all_readmes(self, repos: List[dict]) -> List[dict]:
    """Fetch READMEs for all repos in parallel."""
    tasks = [self.fetch_readme(repo["full_name"]) for repo in repos]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

### Day 3: Code Search Foundation

**Tasks:**
1. Create `fetch_repo_files()` method
2. Fetch file tree for each repo
3. Filter for code files (.py, .js, .rs, .go)
4. Limit to reasonable size (max 100 files per repo)
5. Test file fetching

**Deliverables:**
- File tree fetching (+100 lines)
- File filtering logic

### Day 4: Code Content Indexing

**Tasks:**
1. Fetch file contents for code files
2. Chunk files for RAG (500-line chunks)
3. Index in separate collection: `integration_github_code`
4. Add metadata: repo, file path, language, line numbers
5. Test code search queries

**Deliverables:**
- Code indexing implementation (+120 lines)
- RAG collection with code

### Day 5: Commit History

**Tasks:**
1. Add `fetch_commits()` method (last 50 commits per repo)
2. Extract commit messages, authors, dates, SHAs
3. Index commits in RAG
4. Make commit messages searchable
5. Test commit search

**Deliverables:**
- Commit fetching (+80 lines)
- Commit indexing

---

## Technical Design

### API Endpoints

**Existing:**
- `POST /polly/integrations/sync` - Already works

**New:**
- `GET /polly/github/search-code?query=<pattern>&repo=<name>` - Search code
- `GET /polly/github/commits?repo=<name>&limit=50` - Get commits

### Data Structures

**Incremental Sync State:**
```json
{
  "integration": "github",
  "last_sync": "2026-01-21T10:00:00Z",
  "synced_repos": {
    "user/repo1": {
      "last_updated": "2026-01-20T15:30:00Z",
      "sha": "abc123..."
    }
  }
}
```

**Code File Metadata:**
```python
{
    "content": "def function():\n    pass",
    "metadata": {
        "source": "github",
        "type": "code",
        "repo": "user/repo",
        "file_path": "src/main.py",
        "language": "python",
        "line_start": 1,
        "line_end": 100,
        "updated_at": "2026-01-20T10:00:00Z"
    }
}
```

**Commit Metadata:**
```python
{
    "content": "Fix bug in authentication flow",
    "metadata": {
        "source": "github",
        "type": "commit",
        "repo": "user/repo",
        "sha": "abc123...",
        "author": "Brett Gershon",
        "date": "2026-01-20T10:00:00Z",
        "url": "https://github.com/user/repo/commit/abc123"
    }
}
```

---

## Success Criteria

- ✅ Incremental sync works (only changed repos re-fetched)
- ✅ Parallel README fetching is 10x faster
- ✅ Code search returns relevant results
- ✅ Commit history is searchable
- ✅ No performance degradation with 30+ repos

---

## Future Enhancements

### Phase 6.5: Advanced Code Features
- AST-based code analysis
- Function/class extraction
- Import dependency graphs
- Code quality metrics

### Phase 6.6: Collaboration Features
- PR review comments
- Issue discussions
- Team activity streams
- Repository recommendations

---

## Why This Is Optional

**Current integration is already functional:**
- Repos are indexed
- READMEs are searchable
- Basic sync works

**These enhancements provide:**
- Better performance (faster syncs)
- Deeper code search (within files)
- Richer context (commit history)

**But they're not critical for core functionality.**

---

**Last Updated:** January 21, 2026  
**Status:** Not Started - Optional Enhancement

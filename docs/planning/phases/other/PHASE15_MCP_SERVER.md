# Phase 15: MCP Server Integration

**Status:** 🔜 Planned  
**Priority:** High  
**Estimated Effort:** 5-7 days  
**Dependencies:** None (can start immediately, enhanced by Phases 11-14)

## Overview

Implement a Model Context Protocol (MCP) server that exposes Polly's knowledge base to external AI coding tools like OpenCode, Cursor, Claude Desktop, and Zed. This allows these tools to access all of Polly's integrated knowledge (Obsidian notes, GitHub repos, Context7 docs, learned patterns, mental models) as context for coding tasks.

## Goals

1. **Expose Polly's RAG as MCP resources** - Make all knowledge sources discoverable
2. **Provide search tools via MCP** - Enable semantic search across all sources
3. **Zero fork maintenance** - Use standard MCP protocol, no OpenCode fork needed
4. **Multi-tool support** - Works with any MCP-compatible client
5. **Seamless integration** - OpenCode sees Polly as native context source

## What is MCP?

The **Model Context Protocol** is Anthropic's open standard for connecting AI assistants to external data sources. It defines:

- **Resources:** Read-only data (files, notes, docs)
- **Tools:** Callable functions (search, query, actions)
- **Prompts:** Pre-defined prompt templates

**MCP Architecture:**
```
┌─────────────┐         MCP          ┌─────────────┐
│  OpenCode   │ ◄─── Protocol ────► │   Polly     │
│   (Client)  │      (stdio/HTTP)    │  (Server)   │
└─────────────┘                      └─────────────┘
                                            │
                                            ├─ Obsidian
                                            ├─ GitHub
                                            ├─ Context7
                                            ├─ Calendar
                                            ├─ Patterns
                                            └─ Mental Models
```

## MCP Resources (Read-Only Data)

Polly will expose these resources to MCP clients:

### 1. Obsidian Notes
```
obsidian://notes/{note_path}
obsidian://notes/           (list all)
```
- Exposes all Obsidian vault contents
- Includes markdown with frontmatter
- Preserves wiki-links and backlinks

### 2. GitHub Code
```
github://repos/{owner}/{repo}/files/{path}
github://repos/{owner}/{repo}              (repo info)
github://repos/                            (list all repos)
```
- Code files from synced repositories
- README files and documentation
- Repository metadata

### 3. Context7 Documentation
```
context7://libraries/{library}/docs/{doc_path}
context7://libraries/{library}              (library info)
context7://libraries/                       (list all)
```
- Technical documentation for libraries
- API references
- Examples and guides

### 4. Calendar Events (After Phase 9)
```
calendar://events/upcoming
calendar://events/{date}
calendar://events/search?q={query}
```
- Upcoming meetings and events
- Meeting notes and context
- Schedule awareness

### 5. Learned Patterns (After Phase 13)
```
patterns://learned/query
patterns://learned/code
patterns://learned/conceptual
patterns://learned/workflow
```
- User's organizational habits
- Coding style patterns
- Recurring workflows

### 6. Mental Models (After Phase 14)
```
mental-models://models/{model_name}
mental-models://models/              (list all)
```
- Personal frameworks and philosophies
- Freire, infinite games, constraints as meaning
- Applied thinking patterns

## MCP Tools (Callable Functions)

These tools can be invoked by MCP clients:

### 1. `search_knowledge`
**Search across all Polly knowledge sources**

Parameters:
- `query` (string): Search query
- `sources` (array, optional): Filter by source types
- `limit` (int, optional): Max results (default: 10)

Returns:
```json
{
  "results": [
    {
      "source": "obsidian",
      "title": "Note Title",
      "content": "Relevant excerpt...",
      "score": 0.92,
      "metadata": {
        "path": "notes/project.md",
        "tags": ["work", "ideas"]
      }
    }
  ]
}
```

### 2. `get_code_context`
**Get repository structure and coding patterns**

Parameters:
- `repo` (string): Repository name (e.g., "brettgershon/polly")
- `include_patterns` (bool): Include learned patterns

Returns:
```json
{
  "repo": "brettgershon/polly",
  "structure": {
    "languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "Electron"],
    "directories": ["core/", "integrations/", "interfaces/"]
  },
  "patterns": {
    "coding_style": "Lowercase variables, docstrings, type hints",
    "architecture": "Integration base classes, RAG-first"
  }
}
```

### 3. `get_user_patterns`
**Get learned patterns from user behavior**

Parameters:
- `type` (string, optional): Pattern type (query/code/conceptual/workflow)

Returns:
```json
{
  "patterns": [
    {
      "type": "code",
      "pattern": "Prefer composition over inheritance",
      "confidence": 0.87,
      "examples": 3
    }
  ]
}
```

### 4. `get_mental_model`
**Apply specific mental model to problem**

Parameters:
- `model_name` (string): Mental model to apply
- `context` (string, optional): Problem context

Returns:
```json
{
  "model": "infinite_games",
  "principles": [
    "Focus on continuation over completion",
    "Build for adaptability",
    "Embrace generative constraints"
  ],
  "application": "Suggested approach based on model..."
}
```

### 5. `organize_files` (After Phase 9)
**File system operations via natural language**

Parameters:
- `request` (string): Natural language request
- `context` (object, optional): Current directory, etc.

Returns:
```json
{
  "operations": [...],
  "explanation": "Will organize your Downloads...",
  "requires_confirmation": true
}
```

## MCP Prompts (Templates)

Pre-defined prompts that clients can use:

### 1. `code-with-context`
"Write code that follows my patterns and mental models"

### 2. `refactor-with-philosophy`
"Refactor this code using my mental models (Freire, infinite games, etc.)"

### 3. `search-my-knowledge`
"Search across all my notes, code, and documentation"

### 4. `explain-with-examples`
"Explain using examples from my codebase and notes"

## Implementation Plan

### Day 1-2: Core MCP Protocol

**Create `/interfaces/mcp_server.py`**

```python
"""
MCP Server for Polly
Exposes Polly's knowledge base via Model Context Protocol
"""

from mcp import Server, Resource, Tool
from mcp.server.stdio import stdio_server
import asyncio
from typing import List, Dict, Any

from core.polly import Polly
from integrations import IntegrationManager

class PollyMCPServer:
    def __init__(self):
        self.server = Server("polly")
        self.polly = Polly()
        self.manager = IntegrationManager()
        
        # Register resources
        self.register_resources()
        
        # Register tools
        self.register_tools()
        
        # Register prompts
        self.register_prompts()
    
    def register_resources(self):
        """Register all Polly resources as MCP resources"""
        
        # Obsidian notes
        @self.server.list_resources()
        async def list_obsidian_notes() -> List[Resource]:
            # Return list of all notes as resources
            pass
        
        @self.server.read_resource()
        async def read_obsidian_note(uri: str) -> str:
            # Read specific note content
            pass
        
        # GitHub repos
        @self.server.list_resources()
        async def list_github_repos() -> List[Resource]:
            # Return list of synced repos
            pass
        
        # Context7 docs
        @self.server.list_resources()
        async def list_context7_docs() -> List[Resource]:
            # Return list of library docs
            pass
        
        # Patterns (after Phase 13)
        @self.server.list_resources()
        async def list_patterns() -> List[Resource]:
            # Return learned patterns
            pass
        
        # Mental models (after Phase 14)
        @self.server.list_resources()
        async def list_mental_models() -> List[Resource]:
            # Return available mental models
            pass
    
    def register_tools(self):
        """Register callable tools"""
        
        @self.server.call_tool()
        async def search_knowledge(
            query: str,
            sources: List[str] = None,
            limit: int = 10
        ) -> Dict[str, Any]:
            """Search across all Polly knowledge sources"""
            results = await self.polly.search(
                query=query,
                domains=sources,
                limit=limit
            )
            return {"results": results}
        
        @self.server.call_tool()
        async def get_code_context(
            repo: str,
            include_patterns: bool = True
        ) -> Dict[str, Any]:
            """Get repository structure and patterns"""
            # Implementation
            pass
        
        @self.server.call_tool()
        async def get_user_patterns(
            type: str = None
        ) -> Dict[str, Any]:
            """Get learned user patterns"""
            # Implementation (Phase 13)
            pass
        
        @self.server.call_tool()
        async def get_mental_model(
            model_name: str,
            context: str = None
        ) -> Dict[str, Any]:
            """Apply mental model to context"""
            # Implementation (Phase 14)
            pass
    
    def register_prompts(self):
        """Register prompt templates"""
        
        @self.server.list_prompts()
        async def get_prompts() -> List[Dict]:
            return [
                {
                    "name": "code-with-context",
                    "description": "Write code using my patterns and mental models",
                    "arguments": [
                        {"name": "task", "description": "Coding task", "required": True}
                    ]
                },
                {
                    "name": "search-my-knowledge",
                    "description": "Search across all my knowledge",
                    "arguments": [
                        {"name": "query", "description": "Search query", "required": True}
                    ]
                }
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> str:
            """Generate prompt from template"""
            if name == "code-with-context":
                patterns = await get_user_patterns(type="code")
                return f"""
                Task: {arguments['task']}
                
                Follow these patterns from my codebase:
                {patterns}
                
                Apply these mental models:
                - Continuation over completion
                - Instruments over tracks
                - Constraint as meaning-creation
                """
            # ... other prompts
    
    async def run(self):
        """Start the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

if __name__ == "__main__":
    server = PollyMCPServer()
    asyncio.run(server.run())
```

**Dependencies:**
```bash
pip install mcp
```

### Day 3-4: Resource Implementations

**Implement resource readers for each integration:**

1. **Obsidian Resource Provider** (`/interfaces/mcp_resources/obsidian.py`)
   - List all notes
   - Read note content with metadata
   - Handle wiki-links and backlinks

2. **GitHub Resource Provider** (`/interfaces/mcp_resources/github.py`)
   - List repositories
   - Read code files
   - Expose READMEs and docs

3. **Context7 Resource Provider** (`/interfaces/mcp_resources/context7.py`)
   - List libraries
   - Read documentation
   - Expose API references

4. **Pattern Resource Provider** (`/interfaces/mcp_resources/patterns.py`)
   - List learned patterns (after Phase 13)
   - Read pattern details
   - Include confidence scores

5. **Mental Model Provider** (`/interfaces/mcp_resources/mental_models.py`)
   - List available models (after Phase 14)
   - Read model principles
   - Include application examples

### Day 5: OpenCode Configuration

**Create OpenCode MCP configuration file**

Create `/electron-app/mcp-config.json`:
```json
{
  "mcpServers": {
    "polly": {
      "command": "python",
      "args": ["-m", "interfaces.mcp_server"],
      "cwd": "/Users/brettgershon/polly",
      "env": {
        "POLLY_HOME": "~/.polly",
        "PYTHONPATH": "/Users/brettgershon/polly"
      }
    }
  }
}
```

**Update OpenCode settings** (`~/.config/opencode/config.json`):
```json
{
  "mcp": {
    "configPath": "/Users/brettgershon/polly/electron-app/mcp-config.json"
  }
}
```

### Day 6-7: Testing & Documentation

**Test Script:** `scripts/test_mcp_server.py`
```python
"""
Test MCP Server functionality
"""

import asyncio
from mcp import Client

async def test_mcp_server():
    """Test MCP server resources and tools"""
    
    async with Client("python", ["-m", "interfaces.mcp_server"]) as client:
        # Test listing resources
        print("Testing resource listing...")
        resources = await client.list_resources()
        print(f"Found {len(resources)} resources")
        
        # Test reading a resource
        print("\nTesting resource reading...")
        note = await client.read_resource("obsidian://notes/test.md")
        print(f"Note content: {note[:100]}...")
        
        # Test search tool
        print("\nTesting search tool...")
        results = await client.call_tool(
            "search_knowledge",
            {"query": "React patterns", "limit": 5}
        )
        print(f"Found {len(results['results'])} results")
        
        # Test code context tool
        print("\nTesting code context tool...")
        context = await client.call_tool(
            "get_code_context",
            {"repo": "brettgershon/polly", "include_patterns": True}
        )
        print(f"Repo structure: {context['structure']}")
        
        print("\n✅ All MCP tests passed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

**Documentation:** Create `/docs/mcp_server_setup.md`
```markdown
# Setting Up Polly MCP Server with OpenCode

## Installation

1. Install MCP dependencies:
   ```bash
   pip install mcp
   ```

2. Configure OpenCode to use Polly MCP server:
   ```bash
   # Copy config to OpenCode
   cp electron-app/mcp-config.json ~/.config/opencode/mcp-servers/polly.json
   ```

3. Test the connection:
   ```bash
   python scripts/test_mcp_server.py
   ```

## Usage in OpenCode

Once configured, OpenCode can:

- **Access your notes:** "Search my Obsidian notes for React patterns"
- **Use code context:** "Build a feature following my coding patterns"
- **Apply mental models:** "Refactor this using infinite games thinking"
- **Search everything:** "Find examples of error handling in my codebase and notes"

## Available Resources

- `obsidian://notes/*` - All Obsidian vault notes
- `github://repos/*` - GitHub repository code
- `context7://libraries/*` - Technical documentation
- `patterns://learned/*` - Learned patterns (Phase 13)
- `mental-models://models/*` - Mental models (Phase 14)

## Available Tools

- `search_knowledge(query, sources, limit)` - Semantic search
- `get_code_context(repo, include_patterns)` - Repo structure
- `get_user_patterns(type)` - Learned patterns
- `get_mental_model(model_name, context)` - Apply mental model

## Troubleshooting

### "MCP server not responding"
- Check Python environment: `which python`
- Verify Polly server is running: `python -m interfaces.server`
- Check logs: `~/.polly/logs/mcp_server.log`

### "No resources found"
- Ensure integrations are synced
- Check `~/.polly/integrations_state.json`
- Re-sync: `python scripts/sync_all_integrations.py`
```

## Integration with Existing Features

### With Phase 11 (Multi-Model)
- OpenCode can query which models are available
- Polly MCP server exposes model routing preferences
- Tool: `get_model_preference(task_type)` returns best model for task

### With Phase 12 (Knowledge Graph)
- OpenCode can visualize knowledge connections
- Resource: `graph://nodes/` exposes graph data
- Tool: `get_related_nodes(node_id)` finds connections

### With Phase 13 (Pattern Learning)
- OpenCode accesses learned patterns automatically
- Patterns applied to code generation
- Tool: `get_user_patterns()` returns coding style

### With Phase 14 (Mental Models)
- OpenCode can apply mental models to decisions
- Prompts include mental model principles
- Tool: `get_mental_model(name)` retrieves framework

## API Endpoints (Optional)

In addition to stdio MCP server, optionally expose HTTP endpoints for direct access:

**GET `/mcp/resources`**
List all available resources

**GET `/mcp/resources/{uri}`**
Read specific resource

**POST `/mcp/tools/{tool_name}`**
Call MCP tool directly

This allows non-MCP clients to access Polly's knowledge.

## Security Considerations

1. **Local only** - MCP server runs locally, no network exposure
2. **Read-only resources** - Most resources are read-only
3. **Action confirmation** - File operations require confirmation
4. **Path validation** - All file paths validated for safety
5. **Rate limiting** - Prevent abuse of search tools

## Performance

- **Resource listing:** ~50-100ms (cached)
- **Resource reading:** ~10-20ms per file
- **Search tool:** ~200-500ms (RAG query)
- **Code context:** ~100-200ms (cached)
- **Pattern lookup:** ~50ms (after Phase 13)

## Testing Checklist

- [ ] MCP server starts successfully
- [ ] OpenCode recognizes Polly as MCP server
- [ ] Can list Obsidian notes
- [ ] Can read note content
- [ ] Can search across all sources
- [ ] Can get code context from GitHub repos
- [ ] Can access Context7 documentation
- [ ] Tools return valid JSON responses
- [ ] Error handling works (missing resources, etc.)
- [ ] Performance is acceptable (<500ms for most operations)

## Success Criteria

✅ OpenCode can access all Polly knowledge sources  
✅ Search works across Obsidian, GitHub, Context7  
✅ Code context includes repository structure  
✅ Patterns and mental models accessible (after Phases 13-14)  
✅ Response times under 500ms for most operations  
✅ No fork maintenance required  
✅ Works with other MCP clients (Cursor, Claude Desktop)  

## Future Enhancements

1. **Streaming responses** - For large search results
2. **Caching** - Cache frequently accessed resources
3. **Webhooks** - Notify clients when data changes
4. **Multi-user** - Support multiple MCP clients simultaneously
5. **Authentication** - Add API key auth for remote access
6. **Metrics** - Track MCP usage and performance

## Alternative Clients

This MCP server works with any MCP-compatible client:

- **OpenCode** - Primary use case
- **Cursor** - VS Code fork with AI
- **Claude Desktop** - Anthropic's desktop app
- **Zed** - Collaborative code editor
- **Custom clients** - Build your own MCP client

## Comparison with Other Approaches

| Approach | Complexity | Maintenance | Flexibility | Integration |
|----------|-----------|-------------|-------------|-------------|
| **MCP Server** | Low | Minimal | High | Excellent |
| Embedded Fork | High | High | Medium | Seamless |
| API Only | Very Low | Minimal | Low | Basic |
| Hybrid | Very High | High | Very High | Complex |

MCP Server provides the best balance of simplicity, flexibility, and integration quality.

## Dependencies

- **mcp** (`pip install mcp`) - MCP protocol library
- **asyncio** (built-in) - Async I/O
- All existing Polly integrations

No additional dependencies needed!

## Timeline

- **Day 1-2:** Core MCP protocol implementation (6-8 hours)
- **Day 3-4:** Resource providers for each integration (8-10 hours)
- **Day 5:** OpenCode configuration and testing (4-6 hours)
- **Day 6-7:** Documentation and edge cases (4-6 hours)

**Total:** 22-30 hours (5-7 days)

## Next Steps After Phase 15

1. Use OpenCode with Polly MCP to build features
2. Test with real coding tasks
3. Gather feedback on context quality
4. Enhance tools based on usage patterns
5. Add Phase 13/14 features when ready

---

**Phase 15 turns Polly into a universal knowledge backend for AI coding tools** - no fork needed, works with any MCP client, minimal maintenance! 🎉

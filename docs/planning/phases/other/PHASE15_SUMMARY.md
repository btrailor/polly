# Phase 15: MCP Server - Quick Summary

**Created:** January 21, 2026  
**Status:** Planned  
**Priority:** High (after Phases 11-14)  
**Effort:** 5-7 days

## What Is This?

Phase 15 implements a **Model Context Protocol (MCP) server** that exposes all of Polly's knowledge to external AI coding tools like OpenCode, Cursor, Claude Desktop, and Zed.

## Why MCP Server Instead of OpenCode Fork?

**Option Chosen:** MCP Server (not embedded fork)

**Reasons:**
1. ✅ **Zero maintenance** - No fork to keep synced with upstream
2. ✅ **Works with any MCP client** - OpenCode, Cursor, Claude Desktop, Zed
3. ✅ **Standard protocol** - MCP is becoming industry standard
4. ✅ **Low complexity** - 5-7 days vs 3-4 weeks for embedded fork
5. ✅ **Future-proof** - Protocol is stable and supported

## What Does It Do?

### MCP Resources (Read-Only Data)

Polly exposes these resources to MCP clients:

```
obsidian://notes/*           - All Obsidian vault notes
github://repos/*             - GitHub repository code
context7://libraries/*       - Technical documentation
patterns://learned/*         - Learned patterns (Phase 13)
mental-models://models/*     - Mental models (Phase 14)
calendar://events/*          - Calendar events (Phase 9)
```

### MCP Tools (Callable Functions)

AI coding tools can call these functions:

```python
search_knowledge(query, sources, limit)
# Search across all Polly knowledge sources

get_code_context(repo, include_patterns)
# Get repository structure and learned coding patterns

get_user_patterns(type)
# Get learned patterns (query, code, conceptual, workflow)

get_mental_model(model_name, context)
# Apply personal mental model to problem
```

### MCP Prompts (Templates)

Pre-defined prompts for common tasks:

- `code-with-context` - Write code using my patterns and mental models
- `refactor-with-philosophy` - Refactor using my frameworks
- `search-my-knowledge` - Search across all sources
- `explain-with-examples` - Use my codebase examples

## Use Cases

### In OpenCode:

**Instead of:**
```
"Build a feature that manages user authentication"
```

**With Polly MCP:**
```
"Build a feature that manages user authentication following my coding patterns,
using examples from my GitHub repos, and applying my 'continuation over completion'
mental model"
```

OpenCode can now:
- Access your Obsidian notes about authentication
- Reference actual code patterns from your repos
- Apply your personal mental models
- Use your learned coding style

## Implementation Timeline

**5-7 days total:**

- **Day 1-2:** Core MCP protocol implementation
- **Day 3-4:** Resource providers for each integration
- **Day 5:** OpenCode configuration
- **Day 6-7:** Testing and documentation

## Configuration (After Implementation)

**Step 1:** Install MCP library
```bash
pip install mcp
```

**Step 2:** Configure OpenCode
```json
{
  "mcpServers": {
    "polly": {
      "command": "python",
      "args": ["-m", "interfaces.mcp_server"],
      "cwd": "/Users/brettgershon/polly"
    }
  }
}
```

**Step 3:** Use in OpenCode
OpenCode automatically sees Polly as a context source!

## Benefits

### For You:
- ✅ Code with full context of your knowledge
- ✅ AI follows your patterns automatically
- ✅ Apply your mental models to coding decisions
- ✅ No context switching between apps

### Technical:
- ✅ Works in dev mode (no signed app needed)
- ✅ No fork maintenance (zero ongoing work)
- ✅ Standard protocol (future-proof)
- ✅ Works with multiple tools (not just OpenCode)

## Integration with Other Phases

### Enhanced by Phase 13 (Pattern Learning):
- MCP server exposes learned coding patterns
- OpenCode automatically follows your style
- Tool: `get_user_patterns()` returns patterns

### Enhanced by Phase 14 (Mental Models):
- MCP server exposes mental models
- Apply frameworks to code decisions
- Tool: `get_mental_model(name)` returns principles

### Enhanced by Phase 11 (Multi-Model):
- Can query best model for task
- Tool: `get_model_preference(task_type)`

### Enhanced by Phase 12 (Knowledge Graph):
- Can traverse knowledge connections
- Tool: `get_related_nodes(node_id)`

## Recommended Order

**Build Phases 13-14 first, then Phase 15:**

1. Phase 13: Pattern Learning (1-2 weeks)
2. Phase 14: Mental Models (3-5 days)
3. Phase 12: Knowledge Graph (5-7 days)
4. Phase 11: Multi-Model (7-10 days)
5. **Phase 15: MCP Server (5-7 days)** ← Best when patterns/models exist

This way, the MCP server has rich context to expose.

## Files Created

After implementation, these files will exist:

```
/interfaces/mcp_server.py                    # Main MCP server
/interfaces/mcp_resources/obsidian.py        # Obsidian resource provider
/interfaces/mcp_resources/github.py          # GitHub resource provider
/interfaces/mcp_resources/context7.py        # Context7 resource provider
/interfaces/mcp_resources/patterns.py        # Pattern resource provider
/interfaces/mcp_resources/mental_models.py   # Mental model provider
/electron-app/mcp-config.json                # OpenCode configuration
/docs/mcp_server_setup.md                    # Setup guide
/scripts/test_mcp_server.py                  # Test script
```

## Testing

**Test script:** `python scripts/test_mcp_server.py`

Tests:
- ✅ MCP server starts
- ✅ Resources can be listed
- ✅ Resources can be read
- ✅ Tools can be called
- ✅ Search works across sources
- ✅ OpenCode recognizes Polly

## Next Steps

1. **After Phases 11-14 complete:** Start Phase 15 implementation
2. **Day 1-2:** Build core MCP server
3. **Day 3-4:** Add resource providers
4. **Day 5:** Configure OpenCode
5. **Day 6-7:** Test and document
6. **Use it:** Build features in OpenCode with full Polly context!

## Success Criteria

✅ OpenCode can access all Polly knowledge sources  
✅ Search works across Obsidian, GitHub, Context7  
✅ Patterns and mental models accessible  
✅ Response times under 500ms  
✅ No fork maintenance required  
✅ Works with Cursor, Claude Desktop (bonus)  

## Full Documentation

See **`PHASE15_MCP_SERVER.md`** for complete implementation details including:
- Full code examples
- API specifications
- Detailed day-by-day breakdown
- Security considerations
- Performance benchmarks
- Troubleshooting guide

---

**Phase 15 turns Polly into a universal knowledge backend for AI coding tools!** 🎉

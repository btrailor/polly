# Phase 12: Knowledge Graph Visualization

**Status:** Planning Complete  
**Priority:** High  
**Estimated Effort:** 2.5-3.5 weeks (original 5-7 days + 1-2 weeks for reasoning transparency)  
**Last Updated:** January 24, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Current State](#current-state)
3. [Goals](#goals)
4. [Technical Design](#technical-design)
5. [Implementation Plan](#implementation-plan)
6. [Graph Schema](#graph-schema)
7. [UI/UX Design](#uiux-design)
8. [Testing Strategy](#testing-strategy)
9. [Success Criteria](#success-criteria)
10. [Future Enhancements](#future-enhancements)

---

## Overview

### Vision

Create an interactive, visual knowledge graph that reveals connections between all of Polly's knowledge sources: Obsidian notes, code files, concepts from the knowledge graph, conversations, and GitHub repositories. Users can explore relationships, filter by domain, and discover unexpected connections.

### Key Features

- **Interactive Graph Visualization:** Cytoscape.js-based force-directed layout
- **5 Node Types:** Notes, code files, concepts, conversations, repositories
- **4 Edge Types:** Links, imports, similarity, relationships
- **Rich Filtering:** Domain, node type, date range, keyword search
- **Context Actions:** "Chat with Context", "Open File", "Show Connections"
- **Real-Time Updates:** Graph updates as new data is indexed
- **100-500 Nodes Initially:** Scales to thousands with performance optimizations

### Why Now?

- Polly has rich knowledge sources but no way to visualize connections
- Users want to discover unexpected relationships in their knowledge
- Graph view aligns with Polly's philosophy (continuation, emergence, systems thinking)
- Existing `/learners/graph.py` provides entity/relationship extraction
- RAG system already computes semantic similarity

---

## Current State

### Existing Knowledge Sources

**1. Obsidian Vault**
- 3,508 chunks from 75 files
- Wikilink connections (`[[Note Title]]`)
- Folders map to domains (01-Sigils, 02-Signals, etc.)
- Tags and frontmatter metadata

**2. Codebase**
- 178 chunks from 26 files
- Import relationships (`from X import Y`)
- Function/class definitions
- File dependencies

**3. Knowledge Graph System**
- **File:** `/learners/graph.py` (586 lines)
- Entity extraction (people, tools, concepts, projects)
- Relationship extraction (created_by, uses, connects_to)
- Already stores nodes and edges!

**Current Graph Schema:**
```python
# From /learners/graph.py
{
    "entities": [
        {
            "name": "Paulo Freire",
            "type": "person",
            "context": "Pedagogy of the Oppressed...",
            "mentions": 5
        }
    ],
    "relationships": [
        {
            "source": "Brett",
            "target": "Polly",
            "type": "created",
            "context": "Brett created Polly..."
        }
    ]
}
```

**4. Conversations**
- SQLite database with 6 categories
- Message history
- Timestamps and metadata

**5. GitHub Repos**
- 17 repos synced
- README content
- Repository metadata (language, stars, topics)

### What's Missing

- **No visualization layer** - Data exists but not displayed
- **No user-facing graph page** - Need new "Knowledge" page in UI
- **No graph builder** - Need service to assemble all data sources
- **No cross-source connections** - Notes to code, conversations to notes, etc.

---

## Goals

### Primary Goals

1. **Create Interactive Graph Page:**
   - New "Knowledge" tab in Polly UI
   - Cytoscape.js visualization with force-directed layout
   - Click to zoom, drag nodes, hover for info

2. **Assemble All Data Sources:**
   - Build graph from Obsidian, code, concepts, conversations, repos
   - Extract connections: wikilinks, imports, similarity, relationships
   - Compute 100-500 initial nodes with edges

3. **Implement Rich Filtering:**
   - Filter by domain (Sigils, Signals, Scrolls, Glyphs, Grids)
   - Filter by node type (notes, code, concepts, conversations, repos)
   - Filter by date range
   - Search by keyword

4. **Add Context Actions:**
   - **"Chat with Context"** - Pre-load node content into new conversation
   - **"Open File"** - Open Obsidian note or code file
   - **"Show Connections"** - Highlight connected nodes
   - **"Hide Node"** - Temporarily hide from view

5. **Real-Time Updates:**
   - Graph updates when new notes are synced
   - Graph updates when conversations are created
   - Graph updates when patterns are learned

### Secondary Goals

- Graph export (JSON, GraphML, PNG)
- Graph search (find shortest path between nodes)
- Cluster detection (find communities)
- Time-based graph evolution (see how knowledge grows)
- 3D graph view (optional)

---

## Technical Design

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Electron)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Knowledge Page (new)                            │   │
│  │  • Cytoscape.js canvas                           │   │
│  │  • Filter sidebar                                │   │
│  │  • Node info panel                               │   │
│  │  • Context action menu                           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓ IPC
┌─────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Graph Builder Service                           │   │
│  │  (/core/graph_builder.py)                        │   │
│  │                                                   │   │
│  │  Assembles nodes and edges from:                 │   │
│  │  ┌─────────────────────────────────────────────┐│   │
│  │  │ • Obsidian notes (wikilinks)                ││   │
│  │  │ • Code files (imports)                      ││   │
│  │  │ • Knowledge graph (entities, relationships) ││   │
│  │  │ • Conversations (mentions)                  ││   │
│  │  │ • GitHub repos (dependencies)               ││   │
│  │  │ • RAG similarity (semantic links)           ││   │
│  │  └─────────────────────────────────────────────┘│   │
│  │                                                   │   │
│  │  Output: Cytoscape.js JSON format                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Existing Data Sources                           │   │
│  │  • /core/rag.py (semantic similarity)            │   │
│  │  • /learners/graph.py (entities, relationships)  │   │
│  │  • /integrations/obsidian.py (notes)             │   │
│  │  • /integrations/github.py (repos)               │   │
│  │  • Conversation DB (SQLite)                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
/core/
  graph_builder.py             # NEW: Assembles all data into graph

/electron-app/src/renderer/
  knowledge.html               # NEW: Knowledge page
  knowledge.js                 # NEW: Knowledge page logic
  styles/knowledge.css         # NEW: Knowledge page styles

/electron-app/src/main/
  main.js                      # UPDATE: Add graph IPC handlers
  preload.js                   # UPDATE: Expose graph APIs

/interfaces/
  server.py                    # UPDATE: Add /polly/graph/* endpoints
```

### Node Schema

```typescript
interface GraphNode {
  id: string;                  // Unique identifier
  label: string;               // Display name
  type: "note" | "code" | "concept" | "conversation" | "repo";
  domain: "sigils" | "signals" | "scrolls" | "glyphs" | "grids" | "uncategorized";
  content: string;             // Full text content
  metadata: {
    created_at?: string;
    updated_at?: string;
    tags?: string[];
    path?: string;
    url?: string;
    mentions?: number;
  };
}
```

### Edge Schema

```typescript
interface GraphEdge {
  id: string;                  // Unique identifier
  source: string;              // Source node ID
  target: string;              // Target node ID
  type: "link" | "import" | "similarity" | "relationship";
  weight: number;              // Strength of connection (0-1)
  metadata: {
    context?: string;          // Why this edge exists
    bidirectional?: boolean;   // Can traverse in both directions
  };
}
```

### Cytoscape.js Format

```json
{
  "nodes": [
    {
      "data": {
        "id": "note-123",
        "label": "Pedagogy of the Oppressed",
        "type": "note",
        "domain": "scrolls",
        "content": "...",
        "tags": ["education", "freire"]
      }
    }
  ],
  "edges": [
    {
      "data": {
        "id": "edge-456",
        "source": "note-123",
        "target": "concept-789",
        "type": "relationship",
        "weight": 0.9
      }
    }
  ]
}
```

---

## Implementation Plan

### Day 1: Graph Builder Backend

**Tasks:**
1. Create `/core/graph_builder.py`
2. Implement `GraphBuilder` class
3. Add method to extract Obsidian note nodes
4. Add method to extract code file nodes
5. Add method to extract concept nodes from `/learners/graph.py`
6. Add method to extract conversation nodes from SQLite
7. Add method to extract GitHub repo nodes
8. Add method to compute edges (wikilinks, imports, similarity)

**Deliverables:**
- `/core/graph_builder.py` (500+ lines)

**GraphBuilder Implementation:**

```python
import json
import re
import sqlite3
from typing import List, Dict, Any, Set, Tuple
from pathlib import Path
from collections import defaultdict

class GraphBuilder:
    """Builds knowledge graph from all data sources."""
    
    def __init__(
        self,
        rag_system,
        knowledge_graph,
        obsidian_integration,
        github_integration,
        conversation_db_path: str
    ):
        self.rag = rag_system
        self.kg = knowledge_graph
        self.obsidian = obsidian_integration
        self.github = github_integration
        self.conv_db = conversation_db_path
        
        self.nodes = []
        self.edges = []
        self.node_ids = set()  # Track unique IDs
    
    def build_full_graph(self) -> Dict[str, Any]:
        """Build complete graph from all sources."""
        self.nodes = []
        self.edges = []
        self.node_ids = set()
        
        # Extract nodes
        self._add_obsidian_notes()
        self._add_code_files()
        self._add_concepts()
        self._add_conversations()
        self._add_github_repos()
        
        # Extract edges
        self._add_wikilinks()
        self._add_code_imports()
        self._add_kg_relationships()
        self._add_similarity_edges()
        
        return {
            "nodes": [{"data": n} for n in self.nodes],
            "edges": [{"data": e} for e in self.edges]
        }
    
    def _add_obsidian_notes(self):
        """Add Obsidian notes as nodes."""
        if not self.obsidian or not self.obsidian.vault_path:
            return
        
        vault = Path(self.obsidian.vault_path)
        for md_file in vault.rglob("*.md"):
            # Skip templates and hidden files
            if md_file.name.startswith(".") or "templates" in str(md_file).lower():
                continue
            
            # Read content
            try:
                content = md_file.read_text()
            except:
                continue
            
            # Determine domain from folder
            domain = self._get_domain_from_path(md_file)
            
            # Extract tags
            tags = re.findall(r"#(\w+)", content)
            
            # Create node
            node_id = f"note-{md_file.stem}"
            if node_id not in self.node_ids:
                self.nodes.append({
                    "id": node_id,
                    "label": md_file.stem,
                    "type": "note",
                    "domain": domain,
                    "content": content[:500],  # First 500 chars
                    "path": str(md_file),
                    "tags": tags,
                    "created_at": str(md_file.stat().st_ctime),
                    "updated_at": str(md_file.stat().st_mtime)
                })
                self.node_ids.add(node_id)
    
    def _add_code_files(self):
        """Add code files as nodes."""
        # Get code files from RAG system
        if not hasattr(self.rag, 'chroma_client'):
            return
        
        try:
            # Query code collection
            results = self.rag.code_collection.get()
            
            # Group by file path
            files = defaultdict(list)
            for i, metadata in enumerate(results['metadatas']):
                path = metadata.get('file_path')
                if path:
                    files[path].append(results['documents'][i])
            
            # Create nodes
            for path, chunks in files.items():
                node_id = f"code-{Path(path).stem}"
                if node_id not in self.node_ids:
                    # Determine language
                    ext = Path(path).suffix
                    lang = {
                        '.py': 'python',
                        '.js': 'javascript',
                        '.rs': 'rust',
                        '.go': 'go'
                    }.get(ext, 'unknown')
                    
                    self.nodes.append({
                        "id": node_id,
                        "label": Path(path).name,
                        "type": "code",
                        "domain": "sigils",  # All code is Sigils domain
                        "content": chunks[0] if chunks else "",
                        "path": path,
                        "language": lang,
                        "num_chunks": len(chunks)
                    })
                    self.node_ids.add(node_id)
        except Exception as e:
            print(f"Error adding code files: {e}")
    
    def _add_concepts(self):
        """Add concepts from knowledge graph."""
        if not hasattr(self.kg, 'entities'):
            return
        
        for entity in self.kg.entities:
            node_id = f"concept-{entity['name'].lower().replace(' ', '-')}"
            if node_id not in self.node_ids:
                # Infer domain from entity type
                domain = {
                    'tool': 'sigils',
                    'technology': 'sigils',
                    'person': 'uncategorized',
                    'project': 'grids',
                    'concept': 'grids'
                }.get(entity.get('type'), 'uncategorized')
                
                self.nodes.append({
                    "id": node_id,
                    "label": entity['name'],
                    "type": "concept",
                    "domain": domain,
                    "content": entity.get('context', ''),
                    "entity_type": entity.get('type', 'unknown'),
                    "mentions": entity.get('mentions', 0)
                })
                self.node_ids.add(node_id)
    
    def _add_conversations(self):
        """Add conversations as nodes."""
        try:
            conn = sqlite3.connect(self.conv_db)
            cursor = conn.cursor()
            
            # Get all conversations
            cursor.execute("""
                SELECT id, title, category_id, message_count, created_at, updated_at
                FROM conversations
                WHERE deleted_at IS NULL
            """)
            
            for row in cursor.fetchall():
                conv_id, title, category, msg_count, created, updated = row
                
                node_id = f"conversation-{conv_id}"
                if node_id not in self.node_ids:
                    # Get first message as preview
                    cursor.execute("""
                        SELECT content FROM messages
                        WHERE conversation_id = ?
                        ORDER BY created_at ASC
                        LIMIT 1
                    """, (conv_id,))
                    first_msg = cursor.fetchone()
                    content = first_msg[0] if first_msg else ""
                    
                    self.nodes.append({
                        "id": node_id,
                        "label": title or f"Conversation {conv_id}",
                        "type": "conversation",
                        "domain": category or "uncategorized",
                        "content": content[:500],
                        "message_count": msg_count,
                        "created_at": created,
                        "updated_at": updated
                    })
                    self.node_ids.add(node_id)
            
            conn.close()
        except Exception as e:
            print(f"Error adding conversations: {e}")
    
    def _add_github_repos(self):
        """Add GitHub repos as nodes."""
        if not self.github or not hasattr(self.github, 'repos'):
            return
        
        for repo in self.github.repos:
            node_id = f"repo-{repo['name']}"
            if node_id not in self.node_ids:
                self.nodes.append({
                    "id": node_id,
                    "label": repo['name'],
                    "type": "repo",
                    "domain": "sigils",  # All repos in Sigils domain
                    "content": repo.get('description', ''),
                    "url": repo.get('html_url'),
                    "language": repo.get('language'),
                    "stars": repo.get('stargazers_count', 0),
                    "topics": repo.get('topics', [])
                })
                self.node_ids.add(node_id)
    
    def _add_wikilinks(self):
        """Add wikilink edges between Obsidian notes."""
        # Parse wikilinks from notes
        for node in self.nodes:
            if node['type'] != 'note':
                continue
            
            # Find wikilinks [[Target]]
            wikilinks = re.findall(r'\[\[([^\]]+)\]\]', node.get('content', ''))
            
            for link in wikilinks:
                # Find target node
                target_id = f"note-{link}"
                if target_id in self.node_ids:
                    edge_id = f"link-{node['id']}-{target_id}"
                    self.edges.append({
                        "id": edge_id,
                        "source": node['id'],
                        "target": target_id,
                        "type": "link",
                        "weight": 1.0,
                        "bidirectional": True
                    })
    
    def _add_code_imports(self):
        """Add import edges between code files."""
        for node in self.nodes:
            if node['type'] != 'code':
                continue
            
            # Find imports (Python style)
            imports = re.findall(
                r'from\s+(\w+)\s+import|import\s+(\w+)',
                node.get('content', '')
            )
            
            for match in imports:
                module = match[0] or match[1]
                target_id = f"code-{module}"
                if target_id in self.node_ids:
                    edge_id = f"import-{node['id']}-{target_id}"
                    self.edges.append({
                        "id": edge_id,
                        "source": node['id'],
                        "target": target_id,
                        "type": "import",
                        "weight": 0.8,
                        "bidirectional": False
                    })
    
    def _add_kg_relationships(self):
        """Add relationship edges from knowledge graph."""
        if not hasattr(self.kg, 'relationships'):
            return
        
        for rel in self.kg.relationships:
            source_id = f"concept-{rel['source'].lower().replace(' ', '-')}"
            target_id = f"concept-{rel['target'].lower().replace(' ', '-')}"
            
            if source_id in self.node_ids and target_id in self.node_ids:
                edge_id = f"relationship-{source_id}-{target_id}"
                self.edges.append({
                    "id": edge_id,
                    "source": source_id,
                    "target": target_id,
                    "type": "relationship",
                    "weight": 0.9,
                    "relationship_type": rel.get('type', 'related'),
                    "context": rel.get('context', '')
                })
    
    def _add_similarity_edges(self):
        """Add semantic similarity edges using RAG."""
        # For each note, find similar notes
        for node in self.nodes:
            if node['type'] not in ['note', 'conversation']:
                continue
            
            try:
                # Query RAG for similar content
                results = self.rag.query(
                    node.get('content', '')[:200],
                    n_results=5
                )
                
                for i, metadata in enumerate(results['metadatas'][0]):
                    # Create edge if similarity is high
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    
                    if similarity > 0.7:  # Threshold
                        target_path = metadata.get('file_path') or metadata.get('path')
                        if target_path:
                            target_id = f"note-{Path(target_path).stem}"
                            if target_id in self.node_ids and target_id != node['id']:
                                edge_id = f"similarity-{node['id']}-{target_id}"
                                self.edges.append({
                                    "id": edge_id,
                                    "source": node['id'],
                                    "target": target_id,
                                    "type": "similarity",
                                    "weight": similarity,
                                    "bidirectional": True
                                })
            except Exception as e:
                print(f"Error computing similarity for {node['id']}: {e}")
    
    def _get_domain_from_path(self, path: Path) -> str:
        """Determine domain from file path."""
        path_str = str(path).lower()
        if '01-sigils' in path_str or 'sigils' in path_str:
            return 'sigils'
        elif '02-signals' in path_str or 'signals' in path_str:
            return 'signals'
        elif '03-scrolls' in path_str or 'scrolls' in path_str:
            return 'scrolls'
        elif '04-glyphs' in path_str or 'glyphs' in path_str:
            return 'glyphs'
        elif '05-grids' in path_str or 'grids' in path_str:
            return 'grids'
        else:
            return 'uncategorized'
    
    def filter_graph(
        self,
        domain: str = None,
        node_type: str = None,
        date_range: Tuple[str, str] = None,
        keyword: str = None
    ) -> Dict[str, Any]:
        """Filter graph by various criteria."""
        filtered_nodes = self.nodes
        
        if domain:
            filtered_nodes = [n for n in filtered_nodes if n.get('domain') == domain]
        
        if node_type:
            filtered_nodes = [n for n in filtered_nodes if n.get('type') == node_type]
        
        if keyword:
            keyword_lower = keyword.lower()
            filtered_nodes = [
                n for n in filtered_nodes
                if keyword_lower in n.get('label', '').lower()
                or keyword_lower in n.get('content', '').lower()
            ]
        
        # Filter edges to only include those connecting filtered nodes
        filtered_node_ids = {n['id'] for n in filtered_nodes}
        filtered_edges = [
            e for e in self.edges
            if e['source'] in filtered_node_ids and e['target'] in filtered_node_ids
        ]
        
        return {
            "nodes": [{"data": n} for n in filtered_nodes],
            "edges": [{"data": e} for e in filtered_edges]
        }
```

---

## Reasoning Transparency

### Overview

Reasoning transparency is a core feature that differentiates Polly from black-box AI systems. When Polly creates connections in the knowledge graph, it explains **why** those connections exist. This aligns with the "See how you think" marketing theme and helps users understand their own patterns.

### Goals

1. **Explain every connection** - "Why this connection?" for every edge
2. **Multi-factor analysis** - Show all signals that contributed to the connection
3. **Confidence scoring** - Display connection strength (0.0-1.0)
4. **Interactive exploration** - "Explore from here" mode to traverse reasoning
5. **Learn user patterns** - Surface recurring connection types

### Edge Confidence Scores

Every edge in the knowledge graph has a confidence score representing connection strength:

```typescript
interface Edge {
  id: string;
  source: string; // node ID
  target: string; // node ID
  type: 'wikilink' | 'import' | 'similarity' | 'relationship' | 'pattern';
  
  // Confidence and reasoning
  confidence: number; // 0.0-1.0
  reasoning: ConnectionReasoning;
  
  // Metadata
  createdAt: Date;
  lastStrengthened?: Date; // When user validated this connection
}

interface ConnectionReasoning {
  primaryReason: string; // Human-readable explanation
  contributingFactors: ReasoningFactor[];
  confidenceBreakdown: { [factor: string]: number };
  examples: string[]; // Specific text excerpts that show the connection
}

interface ReasoningFactor {
  type: 'semantic-similarity' | 'keyword-overlap' | 'structural' | 'temporal' | 'user-behavior';
  description: string;
  score: number; // 0.0-1.0
  evidence: string; // Specific evidence for this factor
}
```

**Example Edge with Reasoning:**
```json
{
  "id": "edge-1",
  "source": "note-react-optimization",
  "target": "note-performance-patterns",
  "type": "similarity",
  "confidence": 0.87,
  "reasoning": {
    "primaryReason": "Both notes discuss memoization strategies for React components",
    "contributingFactors": [
      {
        "type": "semantic-similarity",
        "description": "High semantic similarity in content",
        "score": 0.85,
        "evidence": "Both contain similar concepts: useMemo, React.memo, component optimization"
      },
      {
        "type": "keyword-overlap",
        "description": "Shared technical keywords",
        "score": 0.72,
        "evidence": "Common terms: memoization, rendering, performance, React"
      },
      {
        "type": "temporal",
        "description": "Created within same time period",
        "score": 0.65,
        "evidence": "Both created in January 2026 during React refactoring project"
      },
      {
        "type": "user-behavior",
        "description": "Often accessed together",
        "score": 0.78,
        "evidence": "User opened both notes in same session 5 times"
      }
    ],
    "confidenceBreakdown": {
      "semantic-similarity": 0.40,  // 40% of confidence
      "keyword-overlap": 0.25,      // 25% of confidence
      "temporal": 0.15,              // 15% of confidence
      "user-behavior": 0.20          // 20% of confidence
    },
    "examples": [
      "From React Optimization: 'Use React.memo to prevent unnecessary re-renders...'",
      "From Performance Patterns: 'Memoization is critical for React performance...'"
    ]
  }
}
```

### Confidence Calculation

**Formula:**
```python
def calculate_edge_confidence(source_node, target_node, context):
    factors = {
        'semantic_similarity': compute_semantic_similarity(source_node, target_node),
        'keyword_overlap': compute_keyword_overlap(source_node, target_node),
        'structural': compute_structural_similarity(source_node, target_node),
        'temporal': compute_temporal_proximity(source_node, target_node),
        'user_behavior': compute_user_validation(source_node, target_node, context)
    }
    
    # Weighted combination
    weights = {
        'semantic_similarity': 0.40,
        'keyword_overlap': 0.25,
        'structural': 0.15,
        'temporal': 0.10,
        'user_behavior': 0.10
    }
    
    confidence = sum(factors[k] * weights[k] for k in factors)
    
    # User behavior bonus (if user has validated this connection)
    if factors['user_behavior'] > 0.5:
        confidence = min(confidence * 1.2, 1.0)
    
    return confidence
```

**Factor Calculations:**

1. **Semantic Similarity (0.40 weight)**
   - Cosine similarity of embeddings
   - Range: 0.0-1.0
   - High similarity (>0.8) = strong connection

2. **Keyword Overlap (0.25 weight)**
   - Jaccard similarity of significant keywords
   - TF-IDF weighted terms
   - Exclude common words (the, is, and, etc.)

3. **Structural (0.15 weight)**
   - Same domain = +0.3
   - Same tag = +0.2 per tag
   - Same project/folder = +0.4
   - Caps at 1.0

4. **Temporal (0.10 weight)**
   - Created/modified within same week = 0.8
   - Same month = 0.5
   - Same quarter = 0.3
   - Decay over time

5. **User Behavior (0.10 weight, bonus multiplier)**
   - User opened both notes together = +0.3 per occurrence (cap 0.9)
   - User created explicit link between them = 1.0
   - User dismissed suggested connection = 0.0 (blocks edge)

### UI for Reasoning Transparency

#### "Why This Connection?" Modal

Clicking any edge opens reasoning modal:

```
┌──────────────────────────────────────────────────────────┐
│  Why are these notes connected?                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  React Optimization  ←────→  Performance Patterns        │
│                                                           │
│  Connection Strength: ████████░░ 87%                     │
│                                                           │
│  Primary Reason:                                         │
│  Both notes discuss memoization strategies for React     │
│  components. They share technical concepts and were      │
│  created during the same project.                        │
│                                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                           │
│  Contributing Factors:                                   │
│                                                           │
│  🎯 Semantic Similarity (40%)  ████████░░ 85%           │
│     High semantic similarity in content                  │
│     Both contain similar concepts: useMemo, React.memo   │
│                                                           │
│  🔑 Keyword Overlap (25%)  ███████░░░ 72%               │
│     Common terms: memoization, rendering, performance    │
│                                                           │
│  📅 Temporal Proximity (15%)  ██████░░░░ 65%            │
│     Both created in January 2026                         │
│                                                           │
│  👤 User Behavior (20%)  ███████░░░ 78%                 │
│     You've opened these notes together 5 times           │
│                                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                           │
│  Evidence:                                               │
│                                                           │
│  "Use React.memo to prevent unnecessary re-renders..."   │
│     — React Optimization                                 │
│                                                           │
│  "Memoization is critical for React performance..."      │
│     — Performance Patterns                               │
│                                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                           │
│  Actions:                                                │
│  [Explore from React Optimization →]                     │
│  [Explore from Performance Patterns →]                   │
│  [Strengthen Connection] [Dismiss Connection]            │
│                                                           │
│  [Close]                                                 │
└──────────────────────────────────────────────────────────┘
```

#### Edge Hover Tooltip

Hovering over edge shows quick reasoning:

```
┌──────────────────────────────────────────┐
│  Connection: 87% confidence              │
│                                           │
│  Both discuss memoization strategies     │
│  for React components.                   │
│                                           │
│  Click for details                       │
└──────────────────────────────────────────┘
```

#### Graph Filtering by Confidence

Users can filter edges by confidence threshold:

```
┌──────────────────────────────────────────┐
│  Show connections with confidence:       │
│                                           │
│  ◉ High (> 80%)                          │
│  ○ Medium (> 60%)                        │
│  ○ All connections                       │
│                                           │
│  [Apply Filter]                          │
└──────────────────────────────────────────┘
```

### "Explore From Here" Mode

When user clicks "Explore from here", show reasoning-focused traversal:

```
┌──────────────────────────────────────────────────────────┐
│  Exploring from: React Optimization                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Strongest Connections:                                  │
│                                                           │
│  1. Performance Patterns (87%)                           │
│     → Memoization strategies                             │
│     [View Details] [Go There]                            │
│                                                           │
│  2. React Hooks Guide (81%)                              │
│     → useMemo usage examples                             │
│     [View Details] [Go There]                            │
│                                                           │
│  3. Component Architecture (76%)                         │
│     → Optimization patterns                              │
│     [View Details] [Go There]                            │
│                                                           │
│  4. Code Review Notes (68%)                              │
│     → Performance refactoring                            │
│     [View Details] [Go There]                            │
│                                                           │
│  Related Domains: Coding (4 notes), Documentation (1)    │
│  Common Keywords: React, optimization, performance       │
│                                                           │
│  [Back to Graph]                                         │
└──────────────────────────────────────────────────────────┘
```

### Learning User Patterns

Track recurring connection patterns to surface insights:

```typescript
interface ConnectionPattern {
  id: string;
  type: string;
  description: string;
  frequency: number;
  examples: { source: string; target: string; reasoning: string }[];
  confidence: number;
}

// Example patterns Polly learns:
const USER_PATTERNS = [
  {
    type: 'cross-domain-bridge',
    description: 'You often connect Coding notes to Research notes via shared mental models',
    frequency: 23,
    confidence: 0.89
  },
  {
    type: 'temporal-project-clustering',
    description: 'Notes created during the same project week tend to be highly connected',
    frequency: 47,
    confidence: 0.92
  },
  {
    type: 'keyword-signal',
    description: 'When you tag notes with "systems-thinking", they cluster together strongly',
    frequency: 15,
    confidence: 0.85
  }
];
```

**Pattern Insights Panel:**
```
┌──────────────────────────────────────────────────────────┐
│  Your Connection Patterns                                │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Polly has learned these patterns from your knowledge:   │
│                                                           │
│  🔗 Cross-Domain Bridges (23 connections)                │
│     You often connect Coding notes to Research via       │
│     shared mental models. Most common: "systems          │
│     thinking" and "emergence"                            │
│     [View Examples]                                      │
│                                                           │
│  📅 Project Clustering (47 connections)                  │
│     Notes created during the same project week are       │
│     highly connected. Strongest in Jan 2026.             │
│     [View Examples]                                      │
│                                                           │
│  🏷️  Keyword Signals (15 connections)                    │
│     Your "systems-thinking" tag creates tight clusters.  │
│     This tag is a strong connection predictor.           │
│     [View Examples]                                      │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Implementation Changes

**1. Update Edge Schema:**
Add `confidence` and `reasoning` fields to all edges in graph builder.

**2. New Reasoning Engine:**
Create `/core/reasoning_engine.py`:
- `calculate_edge_confidence(source, target, context)`
- `explain_connection(source, target, context)`
- `detect_user_patterns(user_id, graph)`
- `suggest_explorations(node_id, graph)`

**3. API Endpoints:**
```python
@app.post("/polly/graph/explain-connection")
async def explain_connection(source_id: str, target_id: str):
    """Get detailed reasoning for a connection."""
    reasoning = reasoning_engine.explain_connection(source_id, target_id, user_context)
    return {"reasoning": reasoning}

@app.get("/polly/graph/patterns/{user_id}")
async def get_user_patterns(user_id: str):
    """Get learned connection patterns for user."""
    patterns = reasoning_engine.detect_user_patterns(user_id, graph)
    return {"patterns": patterns}

@app.post("/polly/graph/explore/{node_id}")
async def explore_from_node(node_id: str):
    """Get reasoning-focused exploration from a node."""
    explorations = reasoning_engine.suggest_explorations(node_id, graph)
    return {"explorations": explorations}
```

**4. UI Updates:**
- Add edge click handler to show reasoning modal
- Implement hover tooltip with quick reasoning
- Add confidence filter controls
- Build "Explore from here" mode UI
- Create pattern insights panel

### Duration Impact

Adding reasoning transparency increases Phase 12 duration:
- **Original:** 5-7 days
- **With Reasoning:** 2.5-3.5 weeks (adding 1-2 weeks)

**Breakdown:**
- Days 1-5: Original graph implementation
- Days 6-10: Reasoning engine + confidence calculation
- Days 11-14: Reasoning UI (modal, tooltips, exploration mode)
- Days 15-17: Pattern learning + insights (optional polish)

### Marketing Alignment

**"See how you think."**

Reasoning transparency operationalizes this core message. Users don't just see a graph—they understand WHY connections exist and learn their own patterns.

**Key Messages:**
- "Polly explains its reasoning, not just its conclusions"
- "Learn your own thinking patterns through transparent AI"
- "Every connection has a story—Polly tells it"

**Competitive Differentiation:**
- Obsidian/Roam: Show connections but not reasoning
- AI tools: Black-box recommendations
- Polly: Transparent, explainable intelligence

---

### Day 2: API Endpoints

**Tasks:**
1. Add `GET /polly/graph/build` endpoint
2. Add `GET /polly/graph/filter` endpoint
3. Add `POST /polly/graph/node/{id}` endpoint (get node details)
4. Add `POST /polly/graph/neighbors/{id}` endpoint (get connected nodes)
5. Wire up graph builder to API

**Deliverables:**
- Updated `/interfaces/server.py` (+150 lines)

**API Endpoints:**

```python
# In /interfaces/server.py

from core.graph_builder import GraphBuilder

# Initialize graph builder
graph_builder = GraphBuilder(
    rag_system=rag,
    knowledge_graph=knowledge_graph,
    obsidian_integration=obsidian_integration,
    github_integration=github_integration,
    conversation_db_path="~/Library/Application Support/polly/conversations.db"
)

@app.get("/polly/graph/build")
async def build_graph():
    """Build complete knowledge graph."""
    try:
        graph_data = graph_builder.build_full_graph()
        return {
            "success": True,
            "graph": graph_data,
            "stats": {
                "nodes": len(graph_data['nodes']),
                "edges": len(graph_data['edges'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/polly/graph/filter")
async def filter_graph(
    domain: Optional[str] = None,
    node_type: Optional[str] = None,
    keyword: Optional[str] = None
):
    """Filter knowledge graph."""
    try:
        graph_data = graph_builder.filter_graph(
            domain=domain,
            node_type=node_type,
            keyword=keyword
        )
        return {
            "success": True,
            "graph": graph_data,
            "stats": {
                "nodes": len(graph_data['nodes']),
                "edges": len(graph_data['edges'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/polly/graph/node/{node_id}")
async def get_node_details(node_id: str):
    """Get full details for a node."""
    try:
        node = next((n for n in graph_builder.nodes if n['id'] == node_id), None)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return {"success": True, "node": node}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/polly/graph/neighbors/{node_id}")
async def get_node_neighbors(node_id: str):
    """Get all nodes connected to this node."""
    try:
        # Find all edges involving this node
        edges = [
            e for e in graph_builder.edges
            if e['source'] == node_id or e['target'] == node_id
        ]
        
        # Get neighbor node IDs
        neighbor_ids = set()
        for edge in edges:
            if edge['source'] == node_id:
                neighbor_ids.add(edge['target'])
            else:
                neighbor_ids.add(edge['source'])
        
        # Get neighbor nodes
        neighbors = [n for n in graph_builder.nodes if n['id'] in neighbor_ids]
        
        return {
            "success": True,
            "neighbors": neighbors,
            "edges": edges
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Day 3: Frontend - Knowledge Page HTML/CSS

**Tasks:**
1. Create `/electron-app/src/renderer/knowledge.html`
2. Create `/electron-app/src/renderer/styles/knowledge.css`
3. Add Cytoscape.js library to project
4. Design filter sidebar layout
5. Design node info panel layout

**Deliverables:**
- `/electron-app/src/renderer/knowledge.html` (150 lines)
- `/electron-app/src/renderer/styles/knowledge.css` (200 lines)

**HTML Structure:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polly - Knowledge Graph</title>
    <link rel="stylesheet" href="styles/main.css">
    <link rel="stylesheet" href="styles/knowledge.css">
    <script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
</head>
<body>
    <div class="knowledge-container">
        <!-- Filter Sidebar -->
        <div class="filter-sidebar">
            <h2>Filters</h2>
            
            <div class="filter-group">
                <h3>Domain</h3>
                <label><input type="checkbox" value="sigils" checked> 🔐 Sigils</label>
                <label><input type="checkbox" value="signals" checked> 📡 Signals</label>
                <label><input type="checkbox" value="scrolls" checked> 📜 Scrolls</label>
                <label><input type="checkbox" value="glyphs" checked> ✨ Glyphs</label>
                <label><input type="checkbox" value="grids" checked> 🗂️ Grids</label>
            </div>
            
            <div class="filter-group">
                <h3>Node Type</h3>
                <label><input type="checkbox" value="note" checked> 📝 Notes</label>
                <label><input type="checkbox" value="code" checked> 💻 Code</label>
                <label><input type="checkbox" value="concept" checked> 💡 Concepts</label>
                <label><input type="checkbox" value="conversation" checked> 💬 Conversations</label>
                <label><input type="checkbox" value="repo" checked> 📦 Repos</label>
            </div>
            
            <div class="filter-group">
                <h3>Search</h3>
                <input type="text" id="keyword-search" placeholder="Search nodes...">
            </div>
            
            <button id="apply-filters">Apply Filters</button>
            <button id="reset-filters">Reset</button>
        </div>
        
        <!-- Graph Canvas -->
        <div class="graph-canvas" id="cy"></div>
        
        <!-- Node Info Panel -->
        <div class="node-info-panel" id="node-info" style="display: none;">
            <button class="close-btn" id="close-panel">×</button>
            <h2 id="node-title">Node Title</h2>
            <div class="node-metadata">
                <span id="node-type" class="badge">type</span>
                <span id="node-domain" class="badge">domain</span>
            </div>
            <p id="node-content">Content preview...</p>
            
            <div class="node-actions">
                <button id="action-chat">💬 Chat with Context</button>
                <button id="action-open">📂 Open File</button>
                <button id="action-connections">🔗 Show Connections</button>
            </div>
        </div>
    </div>
    
    <script src="knowledge.js"></script>
</body>
</html>
```

### Day 4-5: Frontend - Knowledge Page JavaScript

**Tasks:**
1. Create `/electron-app/src/renderer/knowledge.js`
2. Initialize Cytoscape.js with force-directed layout
3. Implement filter logic
4. Implement node click handlers
5. Implement context menu
6. Implement "Chat with Context" action

**Deliverables:**
- `/electron-app/src/renderer/knowledge.js` (400+ lines)

**Cytoscape.js Initialization:**

```javascript
// knowledge.js

let cy; // Cytoscape instance
let graphData = { nodes: [], edges: [] };

// Initialize graph
async function initGraph() {
    // Fetch graph data
    const response = await window.polly.graphBuild();
    graphData = response.graph;
    
    // Initialize Cytoscape
    cy = cytoscape({
        container: document.getElementById('cy'),
        
        elements: graphData,
        
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'width': 40,
                    'height': 40,
                    'background-color': (ele) => getNodeColor(ele.data('type')),
                    'border-width': 2,
                    'border-color': '#000',
                    'font-size': 12,
                    'text-valign': 'bottom',
                    'text-halign': 'center',
                    'text-margin-y': 5
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': (ele) => ele.data('weight') * 3,
                    'line-color': (ele) => getEdgeColor(ele.data('type')),
                    'target-arrow-color': (ele) => getEdgeColor(ele.data('type')),
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'opacity': 0.6
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 4,
                    'border-color': '#FF6B35'
                }
            }
        ],
        
        layout: {
            name: 'cose',  // Force-directed layout
            animate: true,
            animationDuration: 1000,
            nodeRepulsion: 8000,
            idealEdgeLength: 100,
            edgeElasticity: 100,
            gravity: 1
        }
    });
    
    // Add event listeners
    cy.on('tap', 'node', onNodeClick);
    cy.on('cxttap', 'node', onNodeRightClick);  // Right-click
}

function getNodeColor(type) {
    const colors = {
        'note': '#4A90E2',      // Blue
        'code': '#7B68EE',      // Purple
        'concept': '#F39C12',   // Orange
        'conversation': '#2ECC71', // Green
        'repo': '#E74C3C'       // Red
    };
    return colors[type] || '#95A5A6';
}

function getEdgeColor(type) {
    const colors = {
        'link': '#3498DB',
        'import': '#9B59B6',
        'similarity': '#1ABC9C',
        'relationship': '#E67E22'
    };
    return colors[type] || '#BDC3C7';
}

function onNodeClick(event) {
    const node = event.target;
    showNodeInfo(node.data());
}

function onNodeRightClick(event) {
    const node = event.target;
    showContextMenu(event, node.data());
}

function showNodeInfo(nodeData) {
    const panel = document.getElementById('node-info');
    panel.style.display = 'block';
    
    document.getElementById('node-title').textContent = nodeData.label;
    document.getElementById('node-type').textContent = nodeData.type;
    document.getElementById('node-domain').textContent = nodeData.domain;
    document.getElementById('node-content').textContent = nodeData.content || 'No content available';
    
    // Wire up actions
    document.getElementById('action-chat').onclick = () => chatWithContext(nodeData);
    document.getElementById('action-open').onclick = () => openFile(nodeData);
    document.getElementById('action-connections').onclick = () => showConnections(nodeData);
}

async function chatWithContext(nodeData) {
    // Create new conversation with node content as context
    const conversation = await window.polly.conversationCreate({
        title: `Chat about: ${nodeData.label}`,
        category_id: nodeData.domain
    });
    
    // Pre-load context
    const contextMessage = `I want to discuss: ${nodeData.label}\n\nContext:\n${nodeData.content}`;
    await window.polly.messageAdd(conversation.id, 'user', contextMessage);
    
    // Switch to chat page
    window.location.href = 'index.html';
}

async function openFile(nodeData) {
    if (nodeData.path) {
        if (nodeData.type === 'note') {
            // Open in Obsidian
            const vault = nodeData.path.split('/').find(p => p.includes('.obsidian')).replace('/.obsidian', '');
            const file = nodeData.path.split(vault + '/')[1];
            window.open(`obsidian://open?vault=${vault}&file=${file}`);
        } else if (nodeData.type === 'code') {
            // Open in default editor
            window.polly.openFile(nodeData.path);
        }
    } else if (nodeData.url) {
        // Open URL
        window.open(nodeData.url);
    }
}

async function showConnections(nodeData) {
    // Highlight connected nodes
    cy.elements().removeClass('highlighted');
    
    const node = cy.getElementById(nodeData.id);
    node.addClass('highlighted');
    
    // Highlight neighbors
    node.neighborhood().addClass('highlighted');
}

// Filter logic
async function applyFilters() {
    const domains = Array.from(document.querySelectorAll('.filter-group input[value^="sigils"], input[value^="signals"]'))
        .filter(cb => cb.checked)
        .map(cb => cb.value);
    
    const nodeTypes = Array.from(document.querySelectorAll('.filter-group input[value^="note"], input[value^="code"]'))
        .filter(cb => cb.checked)
        .map(cb => cb.value);
    
    const keyword = document.getElementById('keyword-search').value;
    
    // Fetch filtered graph
    const response = await window.polly.graphFilter({
        domains: domains.length === 5 ? null : domains[0],
        node_type: nodeTypes.length === 5 ? null : nodeTypes[0],
        keyword: keyword || null
    });
    
    // Update graph
    cy.elements().remove();
    cy.add(response.graph);
    cy.layout({ name: 'cose', animate: true }).run();
}

document.getElementById('apply-filters').addEventListener('click', applyFilters);
document.getElementById('reset-filters').addEventListener('click', () => {
    document.querySelectorAll('.filter-group input').forEach(cb => cb.checked = true);
    document.getElementById('keyword-search').value = '';
    initGraph();
});
document.getElementById('close-panel').addEventListener('click', () => {
    document.getElementById('node-info').style.display = 'none';
});

// Initialize on load
initGraph();
```

### Day 6: IPC Handlers & Integration

**Tasks:**
1. Add IPC handlers in `/electron-app/src/main/main.js`
2. Expose graph APIs in preload.js
3. Add "Knowledge" tab to main navigation
4. Test graph building and filtering
5. Test context actions

**Deliverables:**
- Updated `/electron-app/src/main/main.js` (+80 lines)
- Updated `/electron-app/src/main/preload.js` (+15 lines)
- Updated `/electron-app/src/renderer/index.html` (+5 lines for nav)

### Day 7: Testing & Polish

**Tasks:**
1. Test with 100+ nodes
2. Test with 500+ nodes (performance)
3. Test all filter combinations
4. Test context actions
5. Fix UI bugs
6. Add loading states
7. Add error handling

**Deliverables:**
- Bug fixes and polish

---

## Graph Schema

### Node Types

| Type | Icon | Description | Example |
|------|------|-------------|---------|
| **note** | 📝 | Obsidian markdown note | "Pedagogy of the Oppressed" |
| **code** | 💻 | Code file from codebase | "router.py" |
| **concept** | 💡 | Entity from knowledge graph | "Paulo Freire" |
| **conversation** | 💬 | Chat conversation | "Pattern Learning Discussion" |
| **repo** | 📦 | GitHub repository | "polly" |

### Edge Types

| Type | Description | Example | Bidirectional |
|------|-------------|---------|---------------|
| **link** | Wikilink connection | Note A → Note B | Yes |
| **import** | Code import | File A imports File B | No |
| **similarity** | Semantic similarity (RAG) | Note A similar to Note B | Yes |
| **relationship** | Knowledge graph relationship | Person created Project | Depends |

---

## UI/UX Design

### Visual Design

**Node Styling:**
- Notes: Blue circles
- Code: Purple squares
- Concepts: Orange triangles
- Conversations: Green diamonds
- Repos: Red hexagons

**Edge Styling:**
- Links: Blue solid lines
- Imports: Purple dashed lines
- Similarity: Green dotted lines
- Relationships: Orange arrows

**Layout:**
- Force-directed (Cose) for organic clustering
- Domains naturally cluster together
- Connected nodes stay close

### Interactions

**Click:** Show node info panel  
**Right-click:** Context menu  
**Drag:** Move node  
**Scroll:** Zoom in/out  
**Double-click:** Focus on node (hide others)

---

## Testing Strategy

### Unit Tests
- Graph builder node extraction
- Graph builder edge extraction
- Filtering logic

### Integration Tests
- API endpoints return valid graph data
- IPC handlers work correctly
- Cytoscape.js renders graph

### End-to-End Tests
1. Load knowledge page
2. Graph renders with 100+ nodes
3. Apply domain filter → graph updates
4. Click node → info panel appears
5. Click "Chat with Context" → conversation created

---

## Success Criteria

- ✅ Graph visualizes 100-500 nodes from all sources
- ✅ Filter by domain works
- ✅ Filter by node type works
- ✅ Click node shows info panel
- ✅ "Chat with Context" creates conversation
- ✅ Graph updates in real-time when new data is added
- ✅ Performance is smooth (60 FPS) with 500 nodes

---

## Future Enhancements

### Phase 12.5: Advanced Graph Features
- Graph search (shortest path)
- Cluster detection (communities)
- Time-based evolution (see knowledge growth over time)
- 3D graph view

### Phase 12.6: Graph Analytics
- Most connected nodes
- Isolated nodes (orphans)
- Bridge nodes (critical connections)
- Domain distribution

---

**Last Updated:** January 21, 2026  
**Status:** Planning Complete - Ready for Implementation

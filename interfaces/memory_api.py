"""
Memory API Endpoints

REST API for Mem0 adaptive memory operations.

Endpoints:
- POST /api/memory/add - Add a memory
- GET /api/memory/search - Search memories
- GET /api/memory/context - Get formatted context for LLM
- PUT /api/memory/{memory_id} - Update a memory
- DELETE /api/memory/{memory_id} - Delete a memory
- GET /api/memory/all - Get all memories for a user
- DELETE /api/memory/reset - Reset memories
- GET /api/memory/stats - Get memory statistics
- GET /api/memory/persona-preferences - Get persona enrichment preferences (Task #24)
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/memory", tags=["memory"])


# ========== Request/Response Models ==========

class MemoryAddRequest(BaseModel):
    """Request model for adding a memory."""
    content: str = Field(..., description="Memory content")
    user_id: str = Field(default="default", description="User/agent identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class MemoryAddResponse(BaseModel):
    """Response model for adding a memory."""
    success: bool
    memory_id: str
    message: str = "Memory added successfully"


class MemorySearchResponse(BaseModel):
    """Response model for memory search."""
    results: List[Dict[str, Any]]
    count: int
    query: str


class MemoryContextResponse(BaseModel):
    """Response model for memory context."""
    context: str
    memories_count: int


class MemoryUpdateRequest(BaseModel):
    """Request model for updating a memory."""
    content: str = Field(..., description="Updated content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Updated metadata")


class MemoryStatsResponse(BaseModel):
    """Response model for memory statistics."""
    total_memories: int
    by_user: Dict[str, int]
    by_type: Dict[str, int]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None


# ========== Helper Functions ==========

def get_mem0_adapter():
    """
    Get Mem0 adapter instance.
    
    This should be called within endpoint handlers to get the adapter
    from the app state or config.
    
    Raises:
        HTTPException: If Mem0 is not enabled or unavailable
    """
    from fastapi import Request
    from core.memory import get_memory_adapter
    
    # Get config from app state (injected during app startup)
    # For now, we'll load it directly
    try:
        import yaml
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check if Mem0 is enabled
        if config.get('memory', {}).get('provider') != 'mem0':
            raise HTTPException(
                status_code=503,
                detail="Memory provider is not set to 'mem0'. Update config.yaml to enable Mem0."
            )
        
        if not config.get('memory', {}).get('mem0', {}).get('enabled', False):
            raise HTTPException(
                status_code=503,
                detail="Mem0 is not enabled. Set memory.mem0.enabled: true in config.yaml."
            )
        
        adapter = get_memory_adapter(config)
        if adapter is None:
            raise HTTPException(
                status_code=503,
                detail="Failed to initialize Mem0 adapter"
            )
        
        return adapter
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Configuration file not found"
        )
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="mem0ai package not installed. Run: pip install mem0ai>=1.0.0"
        )
    except Exception as e:
        logger.error(f"Failed to get Mem0 adapter: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize memory system: {str(e)}"
        )


# ========== Endpoints ==========

@router.post("/add", response_model=MemoryAddResponse)
async def add_memory(request: MemoryAddRequest):
    """
    Add a memory to Mem0.
    
    Example:
        POST /api/memory/add
        {
            "content": "User prefers Claude Sonnet 4 for code reviews",
            "user_id": "default",
            "metadata": {
                "type": "preference",
                "confidence": 0.9
            }
        }
    """
    try:
        mem0 = get_mem0_adapter()
        
        result = mem0.add_memory(
            content=request.content,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        return MemoryAddResponse(
            success=True,
            memory_id=result.get('id', 'unknown')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=MemorySearchResponse)
async def search_memory(
    query: str = Query(..., description="Search query"),
    user_id: str = Query(default="default", description="User/agent identifier"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum results")
):
    """
    Search memories with semantic similarity.
    
    Example:
        GET /api/memory/search?query=code review preferences&user_id=default&limit=3
    """
    try:
        mem0 = get_mem0_adapter()
        
        results = mem0.search_memory(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        return MemorySearchResponse(
            results=results,
            count=len(results),
            query=query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context", response_model=MemoryContextResponse)
async def get_memory_context(
    query: str = Query(..., description="Context query"),
    user_id: str = Query(default="default", description="User/agent identifier"),
    limit: int = Query(default=3, ge=1, le=10, description="Maximum memories")
):
    """
    Get formatted memory context for LLM prompts.
    
    Example:
        GET /api/memory/context?query=enrichment style&user_id=persona:scribe
    """
    try:
        mem0 = get_mem0_adapter()
        
        context = mem0.get_relevant_context(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        # Count memories in context
        memories_count = context.count('\n') if context else 0
        
        return MemoryContextResponse(
            context=context,
            memories_count=memories_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get memory context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{memory_id}")
async def update_memory(
    memory_id: str,
    request: MemoryUpdateRequest
):
    """
    Update an existing memory.
    
    Example:
        PUT /api/memory/abc123
        {
            "content": "Updated memory content",
            "metadata": {"confidence": 0.95}
        }
    """
    try:
        mem0 = get_mem0_adapter()
        
        result = mem0.update_memory(
            memory_id=memory_id,
            content=request.content,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "Memory updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update memory {memory_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """
    Delete a memory.
    
    Example:
        DELETE /api/memory/abc123
    """
    try:
        mem0 = get_mem0_adapter()
        
        success = mem0.delete_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "Memory deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory {memory_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_memories(
    user_id: str = Query(default="default", description="User/agent identifier")
):
    """
    Get all memories for a user/agent.
    
    Example:
        GET /api/memory/all?user_id=persona:scribe
    """
    try:
        mem0 = get_mem0_adapter()
        
        memories = mem0.get_all_memories(user_id)
        
        return {
            "memories": memories,
            "count": len(memories),
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get all memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset")
async def reset_memories(
    user_id: Optional[str] = Query(default=None, description="User/agent identifier (None = reset all)")
):
    """
    Reset memories. If user_id provided, only that user's memories are cleared.
    
    Example:
        DELETE /api/memory/reset?user_id=persona:scribe
    """
    try:
        mem0 = get_mem0_adapter()
        
        mem0.reset(user_id)
        
        message = f"Reset memories for user_id={user_id}" if user_id else "Reset all memories"
        
        return {
            "success": True,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats():
    """
    Get memory statistics.
    
    Example:
        GET /api/memory/stats
    """
    try:
        mem0 = get_mem0_adapter()
        
        # Get all memories (this is a simplified implementation)
        # In production, you'd want to query the database directly for stats
        all_memories = mem0.get_all_memories("default")
        
        # Count by user_id and type
        by_user = {}
        by_type = {}
        
        for mem in all_memories:
            user_id = mem.get('user_id', 'unknown')
            mem_type = mem.get('metadata', {}).get('type', 'unknown')
            
            by_user[user_id] = by_user.get(user_id, 0) + 1
            by_type[mem_type] = by_type.get(mem_type, 0) + 1
        
        return MemoryStatsResponse(
            total_memories=len(all_memories),
            by_user=by_user,
            by_type=by_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Health Check ==========

@router.get("/health")
async def memory_health():
    """
    Check if Mem0 is available and healthy.
    
    Example:
        GET /api/memory/health
    """
    try:
        mem0 = get_mem0_adapter()
        
        return {
            "status": "healthy",
            "provider": "mem0",
            "message": "Mem0 adaptive memory is available"
        }
        
    except HTTPException as e:
        return {
            "status": "unavailable",
            "provider": "mem0",
            "message": e.detail
        }
    except Exception as e:
        return {
            "status": "error",
            "provider": "mem0",
            "message": str(e)
        }


# ========== Persona Preferences (Task #24) ==========

@router.get("/persona-preferences")
async def get_persona_preferences(
    persona: str = Query(default="scribe", description="Persona name"),
    domain: Optional[str] = Query(default=None, description="Filter by domain"),
    limit: int = Query(default=20, ge=1, le=100, description="Max memories to return"),
):
    """
    Get enrichment preferences stored for a persona.
    
    Returns all memories in the persona's namespace, optionally filtered by domain.
    Groups memories by subtype (template_domain, linking_style, structure_style,
    link_removal, content_expansion, content_condensing, structure_change).
    
    Example:
        GET /api/memory/persona-preferences?persona=scribe
        GET /api/memory/persona-preferences?persona=scribe&domain=scrolls
    """
    try:
        mem0 = get_mem0_adapter()
        user_id = f"persona:{persona}"
        
        # Get all memories for this persona
        all_memories = mem0.get_all_memories(user_id)
        
        if not all_memories:
            return {
                "success": True,
                "persona": persona,
                "total": 0,
                "preferences": {},
                "memories": [],
            }
        
        # Filter by domain if specified
        if domain:
            all_memories = [
                m for m in all_memories
                if m.get('metadata', {}).get('domain', '') == domain
            ]
        
        # Group by subtype
        grouped = {}
        for mem in all_memories:
            metadata = mem.get('metadata', {})
            subtype = metadata.get('subtype', metadata.get('type', 'other'))
            
            if subtype not in grouped:
                grouped[subtype] = []
            
            grouped[subtype].append({
                'id': mem.get('id', ''),
                'memory': mem.get('memory', ''),
                'metadata': metadata,
                'created_at': mem.get('created_at', ''),
            })
        
        # Build summary statistics
        summary = {}
        for subtype, memories in grouped.items():
            summary[subtype] = {
                'count': len(memories),
                'latest': memories[0].get('memory', '') if memories else '',
            }
        
        # Return capped list
        all_formatted = []
        for mem in all_memories[:limit]:
            all_formatted.append({
                'id': mem.get('id', ''),
                'memory': mem.get('memory', ''),
                'metadata': mem.get('metadata', {}),
                'created_at': mem.get('created_at', ''),
            })
        
        return {
            "success": True,
            "persona": persona,
            "total": len(all_memories),
            "summary": summary,
            "memories": all_formatted,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get persona preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

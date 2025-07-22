from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from ..models.research_session import ResearchSession, ResearchSessionCreate
from ..models.hypothesis import Hypothesis
from ..services.claude_service import ClaudeService
from ..services.literature_service import LiteratureService
from ..services.orchestrator_service import AgentOrchestrator
from ..api.websocket import websocket_manager
from ..utils.storage import storage
from ..utils.logger import get_logger

# Create router
router = APIRouter()
logger = get_logger("api")

# Service instances - will be injected as dependencies
claude_service = ClaudeService()
literature_service = LiteratureService(claude_service)  # Pass Claude service for keyword extraction
orchestrator = AgentOrchestrator(claude_service, literature_service, websocket_manager)

# API Testing Endpoints
@router.get("/test/apis")
async def test_apis():
    """Test all external API connections"""
    try:
        # Test Claude API
        claude_status = await claude_service.test_connection()
        
        # Test Perplexity API
        perplexity_status = await literature_service.test_perplexity_connection()
        
        # Test PubMed API
        pubmed_status = await literature_service.test_pubmed_connection()
        
        return {
            "claude": claude_status,
            "perplexity": perplexity_status,
            "pubmed": pubmed_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"API test failed: {e}")
        raise HTTPException(status_code=500, detail=f"API test failed: {str(e)}")

@router.post("/test/claude")
async def test_claude(prompt: str = "Hello, this is a test."):
    """Test Claude API with a custom prompt"""
    try:
        response = await claude_service.generate_text(prompt, max_tokens=100)
        return {
            "success": True,
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Claude test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Claude test failed: {str(e)}")

@router.post("/test/literature")
async def test_literature_search(query: str = "scientific research"):
    """Test literature search APIs"""
    try:
        # Test both services
        perplexity_results = await literature_service.search_academic(query, limit=3)
        pubmed_results = await literature_service.search_pubmed(query, limit=3)
        
        return {
            "success": True,
            "query": query,
            "perplexity_results": len(perplexity_results),
            "pubmed_results": len(pubmed_results),
            "sample_results": {
                "perplexity": perplexity_results[:1],
                "pubmed": pubmed_results[:1]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Literature search test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Literature search test failed: {str(e)}")

# NEW: Domain Detection Endpoint
@router.post("/research/detect-domain")
async def detect_domain(request: dict):
    """Detect research domain from a research question"""
    try:
        research_question = request.get("research_question")
        if not research_question:
            raise HTTPException(status_code=400, detail="Research question is required")
        
        # Use the literature service to detect domain context
        domain_context = await literature_service._detect_domain_context(research_question)
        
        logger.info(f"Detected domain for question '{research_question}': {domain_context}")
        
        return domain_context
        
    except Exception as e:
        logger.error(f"Domain detection failed: {str(e)}")
        # Return default context on error
        return {
            "domain": "general",
            "expert_role": "scientific researcher",
            "field": "scientific research",
            "research_focus": "scientific research",
            "hypothesis_type": "research hypothesis"
        }

# Research Session Endpoints
# Background task to run the orchestrator
async def run_orchestrator_background(session_id: str, research_goal: str, max_iterations: int, hypotheses_per_iteration: int = 1):
    """Run the orchestrator in the background"""
    try:
        logger.info(f"Starting orchestrator for session {session_id}")
        
        # Create and save session
        session_data = {
            "id": session_id,
            "goal": research_goal,
            "status": "running",
            "max_iterations": max_iterations,
            "hypotheses_per_iteration": hypotheses_per_iteration,
            "iteration": 0,
            "hypotheses": []
        }
        await storage.save_research_session(session_data)
        
        # Run the orchestrator
        result = await orchestrator.run_research_session(session_id, research_goal, max_iterations, hypotheses_per_iteration)
        
        logger.info(f"Orchestrator completed for session {session_id}")
        
        # Broadcast completion
        await websocket_manager.broadcast_session_update(
            session_id, "research_completed", {
                "total_hypotheses": len(result.get("hypotheses", [])),
                "status": "completed"
            }
        )
        
    except Exception as e:
        logger.error(f"Orchestrator failed for session {session_id}: {str(e)}")
        
        # Broadcast error
        await websocket_manager.broadcast_session_update(
            session_id, "research_error", {
                "error": str(e),
                "status": "error"
            }
        )

@router.post("/research/start")
async def start_research_session(request: dict, background_tasks: BackgroundTasks):
    """Start a new research session"""
    try:
        research_goal = request.get("research_goal")
        session_id = request.get("session_id")
        max_iterations = request.get("max_iterations", 2)
        hypotheses_per_iteration = request.get("hypotheses_per_iteration", 1)
        
        if not research_goal:
            raise HTTPException(status_code=400, detail="Research goal is required")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        logger.info(f"Starting research session {session_id} with goal: {research_goal}")
        
        # Broadcast session start
        await websocket_manager.broadcast_session_update(
            session_id, "research_started", {
                "research_goal": research_goal,
                "max_iterations": max_iterations,
                "hypotheses_per_iteration": hypotheses_per_iteration
            }
        )
        
        # Start the orchestrator in the background
        background_tasks.add_task(
            run_orchestrator_background, 
            session_id, 
            research_goal, 
            max_iterations,
            hypotheses_per_iteration
        )
        
        return {
            "session_id": session_id,
            "status": "started",
            "research_goal": research_goal,
            "max_iterations": max_iterations,
            "message": "Research session started. Check WebSocket for real-time updates."
        }
        
    except Exception as e:
        logger.error(f"Failed to start research session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start research session: {str(e)}")

async def run_research_session_background(session_id: str):
    """Background task to run the research session"""
    try:
        await orchestrator.run_research_session(session_id)
    except Exception as e:
        logger.error(f"Background research session {session_id} failed: {e}")

@router.get("/research/{session_id}", response_model=Dict[str, Any])
async def get_research_session(session_id: str):
    """Get the current status of a research session"""
    try:
        session_status = await orchestrator.get_session_status(session_id)
        
        if not session_status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.post("/research/{session_id}/cancel")
async def cancel_research_session(session_id: str):
    """Cancel an active research session"""
    try:
        cancelled = await orchestrator.cancel_session(session_id)
        
        if cancelled:
            return {"success": True, "message": "Session cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found or not active")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel session: {str(e)}")

@router.get("/research/sessions/list")
async def list_research_sessions(limit: int = 20):
    """List recent research sessions"""
    try:
        sessions = await storage.list_sessions(limit=limit)
        return {
            "sessions": sessions,
            "count": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.delete("/research/{session_id}")
async def delete_research_session(session_id: str):
    """Delete a research session"""
    try:
        # Cancel if active
        await orchestrator.cancel_session(session_id)
        
        # Delete from storage
        deleted = await storage.delete_session(session_id)
        
        if deleted:
            return {"success": True, "message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

# Hypothesis Endpoints
@router.get("/hypothesis/{hypothesis_id}")
async def get_hypothesis(hypothesis_id: str):
    """Get a specific hypothesis"""
    try:
        hypothesis = await storage.load_hypothesis(hypothesis_id)
        
        if not hypothesis:
            raise HTTPException(status_code=404, detail="Hypothesis not found")
        
        return hypothesis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get hypothesis {hypothesis_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hypothesis: {str(e)}")

# Agent Management Endpoints
@router.post("/agents/generation/test")
async def test_generation_agent(research_goal: str = "Investigate novel approaches for treating acute myeloid leukemia"):
    """Test the generation agent"""
    try:
        logger.info(f"Testing generation agent with goal: {research_goal}")
        
        # Add timestamp to input data
        from datetime import datetime
        input_data = {
            "research_goal": research_goal,
            "iteration": 1,
            "existing_hypotheses": [],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Calling generation agent with input: {list(input_data.keys())}")
        
        result = await orchestrator.generation_agent.execute(input_data)
        
        logger.info(f"Generation agent returned result with keys: {list(result.keys())}")
        
        return {
            "success": True,
            "agent": "generation",
            "result": result
        }
    except Exception as e:
        logger.error(f"Generation agent test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Generation agent test failed: {str(e)}")

@router.post("/agents/reflection/test")
async def test_reflection_agent(hypothesis: str = "Use metformin for treating Alzheimer's disease based on its neuroprotective properties"):
    """Test the reflection agent"""
    try:
        result = await orchestrator.reflection_agent.execute({
            "hypothesis": hypothesis,
            "research_goal": "Test hypothesis evaluation",
            "iteration": 1
        })
        
        return {
            "success": True,
            "agent": "reflection",
            "result": result
        }
    except Exception as e:
        logger.error(f"Reflection agent test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reflection agent test failed: {str(e)}")

@router.post("/agents/ranking/test")
async def test_ranking_agent():
    """Test the ranking agent"""
    try:
        # Create sample hypotheses for testing
        test_hypotheses = [
            {"content": "Use metformin for Alzheimer's treatment", "id": "test1"},
            {"content": "Repurpose aspirin for cancer prevention", "id": "test2"}
        ]
        
        result = await orchestrator.ranking_agent.execute({
            "hypotheses": test_hypotheses,
            "research_goal": "Test ranking system",
            "ranking_method": "direct"
        })
        
        return {
            "success": True,
            "agent": "ranking",
            "result": result
        }
    except Exception as e:
        logger.error(f"Ranking agent test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ranking agent test failed: {str(e)}")

# System Status Endpoints
@router.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    try:
        # Get orchestrator stats
        orchestrator_stats = await orchestrator.get_orchestrator_stats()
        
        # Get WebSocket stats
        websocket_stats = websocket_manager.get_connection_stats()
        
        # Get storage stats
        storage_stats = await storage.get_storage_stats()
        
        return {
            "status": "healthy",
            "orchestrator": orchestrator_stats,
            "websockets": websocket_stats,
            "storage": storage_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/system/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

# Literature Search Endpoints
@router.post("/literature/search")
async def search_literature(query: str, limit: int = 10):
    """Search academic literature"""
    try:
        # Search both sources
        perplexity_results = await literature_service.search_academic(query, limit=limit//2)
        pubmed_results = await literature_service.search_pubmed(query, limit=limit//2)
        
        # Combine results
        all_results = perplexity_results + pubmed_results
        
        return {
            "success": True,
            "query": query,
            "results": all_results,
            "count": len(all_results),
            "sources": {
                "perplexity": len(perplexity_results),
                "pubmed": len(pubmed_results)
            }
        }
    except Exception as e:
        logger.error(f"Literature search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Literature search failed: {str(e)}")

# Cache Management
@router.post("/cache/clear")
async def clear_cache():
    """Clear literature search cache"""
    try:
        cleared_count = storage.cleanup_old_cache(max_age_days=0)  # Clear all cache
        return {
            "success": True,
            "cleared_files": cleared_count,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        storage_stats = await storage.get_storage_stats()
        return {
            "success": True,
            "cache_stats": {
                "cached_literature_count": storage_stats["cached_literature_count"],
                "cache_directory": storage_stats["cache_directory"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

# Import datetime at the top of the file
from datetime import datetime 
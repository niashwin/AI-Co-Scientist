import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from ..agents.generation_agent import GenerationAgent
from ..agents.reflection_agent import ReflectionAgent
from ..agents.ranking_agent import RankingAgent
from ..models.research_session import ResearchSession, ResearchSessionCreate
from ..models.hypothesis import Hypothesis
from ..utils.logger import get_logger
from ..utils.storage import storage

class AgentOrchestrator:
    def __init__(self, claude_service, literature_service, websocket_manager=None):
        self.claude_service = claude_service
        self.literature_service = literature_service
        self.websocket_manager = websocket_manager
        
        # Initialize agents
        self.generation_agent = GenerationAgent(claude_service, literature_service)
        self.reflection_agent = ReflectionAgent(claude_service, literature_service)
        self.ranking_agent = RankingAgent(claude_service)
        
        self.logger = get_logger("orchestrator")
        
        # Active sessions
        self.active_sessions: Dict[str, Dict] = {}
        
        # Configuration
        self.config = {
            "max_iterations": int(os.getenv("MAX_ITERATIONS", 3)),
            "generation_timeout": int(os.getenv("GENERATION_TIMEOUT", 300)),
            "reflection_timeout": int(os.getenv("REFLECTION_TIMEOUT", 180)),
            "ranking_timeout": int(os.getenv("RANKING_TIMEOUT", 120))
        }

    async def run_research_session(self, session_id: str, research_goal: str, max_iterations: int = 3, hypotheses_per_iteration: int = 1):
        """Run the complete multi-agent research workflow"""
        self.logger.info(f"Starting research session {session_id} with goal: {research_goal}")
        
        hypotheses = []
        
        try:
            for iteration in range(1, max_iterations + 1):
                self.logger.info(f"Starting iteration {iteration} for session {session_id}")
                
                # Broadcast iteration start
                if self.websocket_manager:
                    await self.websocket_manager.broadcast_session_update(
                        session_id, "iteration_start", {"iteration": iteration}
                    )
                
                # Generation Phase - generate multiple hypotheses
                self.logger.info(f"Running generation phase - iteration {iteration} (generating {hypotheses_per_iteration} hypotheses)")
                if self.websocket_manager:
                    await self.websocket_manager.broadcast_agent_update(
                        session_id, "generation", "running", {}
                    )
                
                iteration_hypotheses = []
                for hyp_idx in range(hypotheses_per_iteration):
                    generation_result = await self.generation_agent.execute({
                        "research_goal": research_goal,
                        "iteration": iteration,
                        "hypothesis_index": hyp_idx,  # NEW: Index for search variation
                        "total_hypotheses_in_iteration": hypotheses_per_iteration,
                        "existing_hypotheses": hypotheses + iteration_hypotheses,  # Pass full objects for literature access
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    new_hypothesis = {
                        "id": f"hyp_{session_id}_{iteration}_{len(hypotheses) + hyp_idx}",
                        "content": generation_result["hypothesis"],
                        "iteration": iteration,
                        "literature_sources": generation_result["literature_used"],
                        "score": 0.0,
                        "review": "",
                        "rank": None
                    }
                    iteration_hypotheses.append(new_hypothesis)
                
                if self.websocket_manager:
                    await self.websocket_manager.broadcast_agent_update(
                        session_id, "generation", "completed", {"hypotheses": iteration_hypotheses}
                    )
                
                # Reflection Phase - review all generated hypotheses
                self.logger.info(f"Running reflection phase - iteration {iteration} (reviewing {len(iteration_hypotheses)} hypotheses)")
                if self.websocket_manager:
                    await self.websocket_manager.broadcast_agent_update(
                        session_id, "reflection", "running", {}
                    )
                
                for hyp in iteration_hypotheses:
                    reflection_result = await self.reflection_agent.execute({
                        "hypothesis": hyp["content"],
                        "research_goal": research_goal,
                        "iteration": iteration,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    hyp["review"] = reflection_result["review"]
                    hyp["score"] = reflection_result["score"]
                
                if self.websocket_manager:
                    await self.websocket_manager.broadcast_agent_update(
                        session_id, "reflection", "completed", {"reviewed_hypotheses": iteration_hypotheses}
                    )
                
                # Add all iteration hypotheses to the main list
                hypotheses.extend(iteration_hypotheses)
                
                # Ranking Phase (if multiple hypotheses)
                if len(hypotheses) > 1:
                    self.logger.info(f"Running ranking phase - iteration {iteration}")
                    if self.websocket_manager:
                        await self.websocket_manager.broadcast_agent_update(
                            session_id, "ranking", "running", {}
                        )
                    
                    # Prepare hypotheses for ranking
                    ranking_input = []
                    for i, hyp in enumerate(hypotheses):
                        ranking_input.append({
                            "id": hyp["id"],
                            "content": hyp["content"],
                            "score": hyp["score"]
                        })
                    
                    ranking_result = await self.ranking_agent.execute({
                        "hypotheses": ranking_input,
                        "research_goal": research_goal,
                        "iteration": iteration,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Update hypotheses with rankings
                    ranked_hypotheses = ranking_result["ranked_hypotheses"]
                    for rank_idx, ranked_hyp in enumerate(ranked_hypotheses):
                        for hyp in hypotheses:
                            if hyp["id"] == ranked_hyp["id"]:
                                hyp["rank"] = rank_idx + 1
                                break
                    
                    # Sort hypotheses by rank
                    hypotheses = sorted(hypotheses, key=lambda x: x.get("rank", 999))
                    
                    if self.websocket_manager:
                        await self.websocket_manager.broadcast_agent_update(
                            session_id, "ranking", "completed", {"ranked_hypotheses": hypotheses}
                        )
                
                self.logger.info(f"Completed iteration {iteration} for session {session_id}")
                
                # Short delay between iterations
                await asyncio.sleep(2)
            
            self.logger.info(f"Completed research session {session_id} with {len(hypotheses)} hypotheses")
            
            return {
                "session_id": session_id,
                "research_goal": research_goal,
                "hypotheses": hypotheses,
                "total_iterations": max_iterations,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error in research session {session_id}: {str(e)}")
            raise e

    async def create_research_session(self, session_create: ResearchSessionCreate) -> ResearchSession:
        """Create a new research session"""
        session_id = str(uuid.uuid4())
        
        session = ResearchSession(
            id=session_id,
            goal=session_create.goal,
            status="pending",
            max_iterations=session_create.max_iterations,
            iteration=0,
            hypotheses=[]
        )
        
        # Store session
        self.active_sessions[session_id] = session.dict()
        
        return session 
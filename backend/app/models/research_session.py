from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
from .hypothesis import Hypothesis

class ResearchSession(BaseModel):
    id: str
    goal: str
    status: Literal['pending', 'running', 'completed', 'error'] = 'pending'
    hypotheses: List[Hypothesis] = []
    iteration: int = 0
    max_iterations: int = 3
    hypotheses_per_iteration: int = 1
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ResearchSessionCreate(BaseModel):
    goal: str
    max_iterations: int = 3
    hypotheses_per_iteration: int = 1

class AgentProgress(BaseModel):
    current_agent: str
    iteration: int
    progress: dict = {
        'generation': 'pending',
        'reflection': 'pending', 
        'ranking': 'pending'
    }

class QualityMetrics(BaseModel):
    iteration: int
    overall: float
    novelty: float
    feasibility: float
    relevance: float
    specificity: float 
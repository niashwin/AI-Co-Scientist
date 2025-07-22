from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Hypothesis(BaseModel):
    id: str
    content: str
    score: float = 0.0
    iteration: int
    review: str = ""
    citations: List[str] = []
    literature_sources: List[dict] = []
    created_at: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HypothesisCreate(BaseModel):
    content: str
    iteration: int
    literature_sources: List[dict] = []

class HypothesisUpdate(BaseModel):
    score: Optional[float] = None
    review: Optional[str] = None
    citations: Optional[List[str]] = None 
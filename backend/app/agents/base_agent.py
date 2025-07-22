from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
import logging
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, name: str, claude_service, literature_service):
        self.name = name
        self.claude_service = claude_service
        self.literature_service = literature_service
        self.logger = logging.getLogger(f"agent.{name}")
        self.execution_history = []
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary function"""
        pass
    
    async def log_execution(self, input_data: Dict, output_data: Dict):
        """Log agent execution for monitoring and debugging"""
        execution_record = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "input_size": len(str(input_data)),
            "output_size": len(str(output_data)),
            "success": True
        }
        
        self.execution_history.append(execution_record)
        self.logger.info(f"{self.name} executed: {len(str(output_data))} chars output")
    
    async def log_error(self, input_data: Dict, error: Exception):
        """Log agent execution errors"""
        error_record = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "input_size": len(str(input_data)),
            "error": str(error),
            "success": False
        }
        
        self.execution_history.append(error_record)
        self.logger.error(f"{self.name} failed: {str(error)}")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics for this agent"""
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for record in self.execution_history if record["success"])
        
        return {
            "agent": self.name,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "last_execution": self.execution_history[-1]["timestamp"] if self.execution_history else None
        } 
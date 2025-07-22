import os
import asyncio
from typing import Optional, Dict, Any
import anthropic
from anthropic import AsyncAnthropic

class ClaudeService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = AsyncAnthropic(api_key=api_key)
        # Use the correct model name for Claude Sonnet-4
        self.model = "claude-3-5-sonnet-20241022"
    
    async def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Generate text using Claude Sonnet-4 with Messages API"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    async def generate_hypothesis(self, prompt: str, research_goal: str) -> str:
        """Generate a research hypothesis"""
        formatted_prompt = f"Research Goal: {research_goal}\n\n{prompt}"
        return await self.generate_text(formatted_prompt, max_tokens=2000, temperature=0.7)

    async def review_hypothesis(self, hypothesis: str, criteria: str) -> Dict[str, Any]:
        """Review and score a hypothesis"""
        prompt = f"""
        Review this research hypothesis based on the following criteria:
        {criteria}
        
        Hypothesis: {hypothesis}
        
        Please provide:
        1. A detailed review (2-3 sentences)
        2. A score from 0.0 to 1.0 (where 1.0 is excellent)
        3. Key strengths and weaknesses
        
        Format your response as:
        SCORE: [0.0-1.0]
        REVIEW: [detailed review]
        STRENGTHS: [key strengths]
        WEAKNESSES: [key weaknesses]
        """
        
        response = await self.generate_text(prompt, max_tokens=1000, temperature=0.3)
        
        # Parse the response
        lines = response.split('\n')
        score = 0.5
        review = ""
        strengths = ""
        weaknesses = ""
        
        for line in lines:
            if line.startswith('SCORE:'):
                try:
                    score = float(line.split(':', 1)[1].strip())
                except:
                    score = 0.5
            elif line.startswith('REVIEW:'):
                review = line.split(':', 1)[1].strip()
            elif line.startswith('STRENGTHS:'):
                strengths = line.split(':', 1)[1].strip()
            elif line.startswith('WEAKNESSES:'):
                weaknesses = line.split(':', 1)[1].strip()
        
        return {
            "score": score,
            "review": review,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    async def rank_hypotheses(self, hypothesis1: str, hypothesis2: str, criteria: str = "") -> Dict[str, Any]:
        """Compare and rank two hypotheses"""
        prompt = f"""
        Compare these two research hypotheses and determine which is better:
        
        Hypothesis A: {hypothesis1}
        
        Hypothesis B: {hypothesis2}
        
        Criteria: {criteria if criteria else "Novelty, feasibility, scientific rigor, potential impact"}
        
        Respond with:
        WINNER: [A or B]
        REASONING: [brief explanation]
        """
        
        response = await self.generate_text(prompt, max_tokens=500, temperature=0.3)
        
        # Parse response
        winner = "A"
        reasoning = ""
        
        lines = response.split('\n')
        for line in lines:
            if line.startswith('WINNER:'):
                winner = line.split(':', 1)[1].strip()
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
        
        return {
            "winner": winner,
            "reasoning": reasoning
        }

    async def test_connection(self) -> bool:
        """Test if the Claude API is working"""
        try:
            response = await self.generate_text("Hello, this is a test.", max_tokens=10)
            return len(response) > 0
        except:
            return False 
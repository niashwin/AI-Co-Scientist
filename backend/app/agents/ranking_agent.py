import time
from .base_agent import BaseAgent
from typing import Dict, Any, List

class RankingAgent(BaseAgent):
    def __init__(self, claude_service):
        super().__init__("RankingAgent", claude_service, None)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the ranking agent's hypothesis comparison workflow"""
        try:
            hypotheses = input_data["hypotheses"]
            research_goal = input_data["research_goal"]
            iteration = input_data.get("iteration", 1)
            
            self.logger.info(f"Starting ranking for iteration {iteration} with {len(hypotheses)} hypotheses")
            
            if len(hypotheses) < 2:
                # No ranking needed for single hypothesis
                result = {
                    "ranked_hypotheses": hypotheses,
                    "ranking_rationale": "Only one hypothesis available, no ranking performed",
                    "pairwise_comparisons": [],
                    "iteration": iteration,
                    "agent": self.name
                }
            else:
                # Perform pairwise comparisons and ranking
                self.logger.info("Performing pairwise comparisons...")
                ranked_hypotheses, comparisons = await self._rank_hypotheses(hypotheses, research_goal)
                
                result = {
                    "ranked_hypotheses": ranked_hypotheses,
                    "ranking_rationale": await self._generate_ranking_rationale(ranked_hypotheses, research_goal),
                    "pairwise_comparisons": comparisons,
                    "iteration": iteration,
                    "agent": self.name
                }
            
            await self.log_execution(input_data, result)
            return result
            
        except Exception as e:
            await self.log_error(input_data, e)
            raise Exception(f"Ranking agent execution failed: {str(e)}")
    
    async def _rank_hypotheses(self, hypotheses: List[Dict], research_goal: str) -> tuple[List[Dict], List[Dict]]:
        """Rank hypotheses using pairwise comparisons"""
        
        # Initialize scores
        hypothesis_scores = {i: 0 for i in range(len(hypotheses))}
        comparisons = []
        
        # Perform pairwise comparisons
        for i in range(len(hypotheses)):
            for j in range(i + 1, len(hypotheses)):
                comparison = await self._compare_hypotheses(
                    hypotheses[i], hypotheses[j], research_goal
                )
                
                comparisons.append({
                    "hypothesis_a_index": i,
                    "hypothesis_b_index": j,
                    "winner": comparison["winner"],
                    "reasoning": comparison["reasoning"]
                })
                
                # Update scores based on comparison
                if comparison["winner"] == "A":
                    hypothesis_scores[i] += 1
                elif comparison["winner"] == "B":
                    hypothesis_scores[j] += 1
                else:  # Tie
                    hypothesis_scores[i] += 0.5
                    hypothesis_scores[j] += 0.5
        
        # Sort hypotheses by score
        ranked_indices = sorted(hypothesis_scores.keys(), key=lambda x: hypothesis_scores[x], reverse=True)
        
        # Create ranked list with scores
        ranked_hypotheses = []
        for rank, idx in enumerate(ranked_indices):
            hypothesis = hypotheses[idx].copy()
            hypothesis["rank"] = rank + 1
            hypothesis["ranking_score"] = hypothesis_scores[idx]
            ranked_hypotheses.append(hypothesis)
        
        return ranked_hypotheses, comparisons
    
    async def _compare_hypotheses(self, hypothesis_a: Dict, hypothesis_b: Dict, research_goal: str) -> Dict[str, Any]:
        """Compare two hypotheses and determine which is better"""
        
        criteria = """
        1. Scientific rigor and validity
        2. Novelty and innovation potential
        3. Feasibility for experimental testing
        4. Clinical relevance and potential impact
        5. Specificity and actionability
        """
        
        prompt = f"""
Compare these two research hypotheses and determine which is better for the given research goal.

Research Goal: {research_goal}

Hypothesis A:
{hypothesis_a.get('content', hypothesis_a.get('hypothesis', 'Unknown hypothesis'))}

Hypothesis B: 
{hypothesis_b.get('content', hypothesis_b.get('hypothesis', 'Unknown hypothesis'))}

Evaluation Criteria:
{criteria}

Consider the overall scientific merit, feasibility, and potential impact of each hypothesis.

Respond with:
WINNER: [A, B, or TIE]
REASONING: [2-3 sentences explaining your decision based on the criteria]

If the hypotheses are very similar in quality, respond with TIE.
"""
        
        try:
            response = await self.claude_service.generate_text(prompt, max_tokens=500, temperature=0.3)
            
            # Parse response
            winner = "TIE"
            reasoning = ""
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('WINNER:'):
                    winner_text = line.split(':', 1)[1].strip().upper()
                    if winner_text in ['A', 'B', 'TIE']:
                        winner = winner_text
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
                elif reasoning and line:  # Continue building reasoning
                    reasoning += " " + line
            
            return {
                "winner": winner,
                "reasoning": reasoning.strip()
            }
            
        except Exception as e:
            self.logger.error(f"Claude hypothesis comparison failed: {str(e)}")
            # Return fallback comparison
            return {
                "winner": "TIE",
                "reasoning": "Unable to perform detailed comparison due to API limitations."
            }
    
    async def _generate_ranking_rationale(self, ranked_hypotheses: List[Dict], research_goal: str) -> str:
        """Generate an overall rationale for the ranking"""
        
        if len(ranked_hypotheses) <= 1:
            return "Only one hypothesis available for ranking."
        
        top_hypothesis = ranked_hypotheses[0]
        
        prompt = f"""
Provide a brief rationale for why this hypothesis ranked highest among the alternatives for the research goal.

Research Goal: {research_goal}

Top-Ranked Hypothesis:
{top_hypothesis.get('content', top_hypothesis.get('hypothesis', 'Unknown hypothesis'))}

Ranking Score: {top_hypothesis.get('ranking_score', 'Unknown')}/{len(ranked_hypotheses)-1} wins

Provide 2-3 sentences explaining what makes this hypothesis stand out in terms of:
- Scientific merit
- Innovation potential  
- Feasibility
- Clinical relevance

Rationale:
"""
        
        try:
            rationale = await self.claude_service.generate_text(prompt, max_tokens=300, temperature=0.3)
            return rationale.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate ranking rationale: {str(e)}")
            return f"Hypothesis ranked highest based on pairwise comparisons ({top_hypothesis.get('ranking_score', 'Unknown')} wins)." 
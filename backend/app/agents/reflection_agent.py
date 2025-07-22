import time
from .base_agent import BaseAgent
from typing import Dict, Any, List

class ReflectionAgent(BaseAgent):
    def __init__(self, claude_service, literature_service):
        super().__init__("ReflectionAgent", claude_service, literature_service)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the reflection agent's hypothesis review workflow"""
        try:
            hypothesis = input_data["hypothesis"]
            research_goal = input_data["research_goal"]
            iteration = input_data.get("iteration", 1)
            
            self.logger.info(f"Starting reflection for iteration {iteration}")
            
            # Review the hypothesis using Claude
            self.logger.info("Reviewing hypothesis with Claude...")
            review_result = await self._review_hypothesis(hypothesis, research_goal)
            
            # Assess quality dimensions
            self.logger.info("Assessing quality dimensions...")
            quality_assessment = await self._assess_quality_dimensions(hypothesis, research_goal)
            
            result = {
                "review": review_result["review"],
                "score": review_result["score"],
                "strengths": review_result["strengths"],
                "weaknesses": review_result["weaknesses"],
                "quality_dimensions": quality_assessment,
                "iteration": iteration,
                "agent": self.name,
                "hypothesis_id": input_data.get("hypothesis_id"),
                "timestamp": input_data.get("timestamp")
            }
            
            await self.log_execution(input_data, result)
            return result
            
        except Exception as e:
            await self.log_error(input_data, e)
            raise Exception(f"Reflection agent execution failed: {str(e)}")
    
    async def _review_hypothesis(self, hypothesis: str, research_goal: str) -> Dict[str, Any]:
        """Review and score a hypothesis using Claude"""
        
        criteria = """
        1. Scientific Validity: Is the hypothesis based on sound scientific principles?
        2. Novelty: Does this represent a novel research approach?
        3. Feasibility: Is this hypothesis practically testable and implementable?
        4. Impact Potential: Would this have meaningful impact if successful?
        5. Specificity: Is the hypothesis specific enough to be actionable?
        """
        
        prompt = f"""
You are a senior scientific researcher reviewing a research hypothesis. Provide a thorough, constructive review.

Research Goal: {research_goal}

Hypothesis to Review:
{hypothesis}

Evaluation Criteria:
{criteria}

Please provide:
1. A detailed review (3-4 sentences) highlighting the main scientific merits and concerns
2. A score from 0.0 to 1.0 (where 1.0 is excellent, 0.0 is poor)
3. Key strengths (2-3 specific points)
4. Key weaknesses or areas for improvement (2-3 specific points)

Format your response as:
SCORE: [0.0-1.0]
REVIEW: [detailed review]
STRENGTHS: [bullet points of strengths]
WEAKNESSES: [bullet points of weaknesses]
"""
        
        try:
            response = await self.claude_service.generate_text(prompt, max_tokens=1000, temperature=0.3)
            
            # Parse the response
            lines = response.split('\n')
            score = 0.5
            review = ""
            strengths = ""
            weaknesses = ""
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('SCORE:'):
                    try:
                        score_text = line.split(':', 1)[1].strip()
                        score = float(score_text)
                        score = max(0.0, min(1.0, score))  # Clamp to 0-1 range
                    except:
                        score = 0.5
                elif line.startswith('REVIEW:'):
                    current_section = 'review'
                    review = line.split(':', 1)[1].strip()
                elif line.startswith('STRENGTHS:'):
                    current_section = 'strengths'
                    strengths = line.split(':', 1)[1].strip()
                elif line.startswith('WEAKNESSES:'):
                    current_section = 'weaknesses'
                    weaknesses = line.split(':', 1)[1].strip()
                elif line and current_section:
                    # Continue building the current section
                    if current_section == 'review':
                        review += " " + line
                    elif current_section == 'strengths':
                        strengths += " " + line
                    elif current_section == 'weaknesses':
                        weaknesses += " " + line
            
            return {
                "score": score,
                "review": review.strip(),
                "strengths": strengths.strip(),
                "weaknesses": weaknesses.strip()
            }
            
        except Exception as e:
            self.logger.error(f"Claude hypothesis review failed: {str(e)}")
            # Return fallback review
            return {
                "score": 0.5,
                "review": "Unable to generate detailed review due to API limitations. Manual review recommended.",
                "strengths": "Hypothesis addresses the research goal",
                "weaknesses": "Requires detailed scientific validation"
            }
    
    async def _assess_quality_dimensions(self, hypothesis: str, research_goal: str) -> Dict[str, float]:
        """Assess hypothesis on multiple quality dimensions"""
        
        dimensions = {
            "novelty": "How novel and innovative is this research approach?",
            "feasibility": "How feasible is this hypothesis for experimental testing?", 
            "relevance": "How relevant is this to the stated research goal?",
            "specificity": "How specific and actionable is this hypothesis?"
        }
        
        dimension_scores = {}
        
        for dimension, question in dimensions.items():
            try:
                prompt = f"""
Rate this research hypothesis on {dimension} using the question: {question}

Hypothesis: {hypothesis}
Research Goal: {research_goal}

Provide a score from 0.0 to 1.0 where:
- 0.0-0.3: Poor
- 0.4-0.6: Moderate  
- 0.7-0.8: Good
- 0.9-1.0: Excellent

Return only the numerical score (e.g., 0.7).
"""
                
                response = await self.claude_service.generate_text(prompt, max_tokens=50, temperature=0.1)
                
                try:
                    score = float(response.strip().split()[0])
                    dimension_scores[dimension] = max(0.0, min(1.0, score))
                except:
                    dimension_scores[dimension] = 0.5
                    
            except Exception as e:
                self.logger.warning(f"Failed to assess {dimension}: {str(e)}")
                dimension_scores[dimension] = 0.5
        
        return dimension_scores
    
    async def comparative_review(self, hypotheses: List[Dict[str, Any]], research_goal: str) -> Dict[str, Any]:
        """Compare multiple hypotheses and provide comparative analysis"""
        if len(hypotheses) < 2:
            raise ValueError("Need at least 2 hypotheses for comparison")
        
        # Review each hypothesis individually
        reviews = []
        for i, hyp_data in enumerate(hypotheses):
            hypothesis = hyp_data.get("hypothesis", hyp_data.get("content", ""))
            review = await self.execute({
                "hypothesis": hypothesis,
                "research_goal": research_goal,
                "iteration": i + 1
            })
            reviews.append(review)
        
        # Generate comparative analysis
        comparison = await self._generate_comparative_analysis(hypotheses, reviews, research_goal)
        
        return {
            "individual_reviews": reviews,
            "comparative_analysis": comparison,
            "ranked_order": sorted(range(len(reviews)), key=lambda i: reviews[i]["score"], reverse=True),
            "best_hypothesis_index": max(range(len(reviews)), key=lambda i: reviews[i]["score"])
        }
    
    async def _generate_comparative_analysis(self, hypotheses: List[Dict], reviews: List[Dict], research_goal: str) -> str:
        """Generate comparative analysis of multiple hypotheses"""
        
        hypothesis_summaries = []
        for i, (hyp_data, review) in enumerate(zip(hypotheses, reviews)):
            hypothesis = hyp_data.get("hypothesis", hyp_data.get("content", ""))
            summary = f"Hypothesis {i+1} (Score: {review['score']:.2f}): {hypothesis[:200]}..."
            hypothesis_summaries.append(summary)
        
        prompt = f"""
        Provide a comparative analysis of these research hypotheses:

        Research Goal: {research_goal}

        Hypotheses and Scores:
        {chr(10).join(hypothesis_summaries)}

        Please provide:
        1. Overall comparison of the approaches
        2. Relative strengths and weaknesses
        3. Which hypothesis shows the most promise and why
        4. Potential for combining insights from multiple hypotheses

        Keep the analysis concise but insightful.
        """
        
        try:
            return await self.claude_service.generate_text(prompt, max_tokens=1000, temperature=0.4)
        except Exception as e:
            self.logger.warning(f"Could not generate comparative analysis: {e}")
            return "Comparative analysis could not be generated." 
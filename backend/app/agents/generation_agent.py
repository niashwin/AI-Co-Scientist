import time
import uuid
from .base_agent import BaseAgent
from typing import Dict, Any, List
import asyncio

class GenerationAgent(BaseAgent):
    def __init__(self, claude_service, literature_service):
        super().__init__("GenerationAgent", claude_service, literature_service)
        # Pass Claude service to literature service for keyword extraction
        self.literature_service.claude_service = claude_service
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generation agent's workflow"""
        try:
            research_goal = input_data["research_goal"]
            iteration = input_data.get("iteration", 1)
            hypothesis_index = input_data.get("hypothesis_index", 0)
            total_hypotheses = input_data.get("total_hypotheses_in_iteration", 1)
            existing_hypotheses = input_data.get("existing_hypotheses", [])
            
            self.logger.info(f"Starting generation for iteration {iteration}, hypothesis {hypothesis_index + 1}/{total_hypotheses}")
            
            # Step 1: Literature search using LLM-based strategy with variation
            self.logger.info(f"Searching literature with LLM-based strategy (variant {hypothesis_index + 1})...")
            literature = await self._search_literature_with_strategy(research_goal, iteration, existing_hypotheses, hypothesis_index, total_hypotheses)
            self.logger.info(f"Literature search returned {len(literature) if literature else 0} results")
            
            # Step 2: Generate hypothesis using Claude
            self.logger.info("Generating hypothesis with Claude...")
            
            # Extract content strings for duplication avoidance
            existing_contents = []
            for hyp in existing_hypotheses:
                if isinstance(hyp, dict):
                    existing_contents.append(hyp.get("content", str(hyp)))
                else:
                    existing_contents.append(str(hyp))
            
            hypothesis = await self._generate_hypothesis(research_goal, literature, existing_contents)
            
            # Step 3: Extract key information
            result = {
                "hypothesis": hypothesis,
                "literature_used": literature[:8] if literature else [],  # Return full literature objects with complete metadata
                "iteration": iteration,
                "agent": self.name,
                "timestamp": input_data.get("timestamp"),
                "research_goal": research_goal
            }
            
            await self.log_execution(input_data, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Generation agent execution error: {str(e)}")
            await self.log_error(input_data, e)
            raise Exception(f"Generation agent execution failed: {str(e)}")
    
    async def _search_literature_with_strategy(self, research_goal: str, iteration: int, existing_hypotheses: List, hypothesis_index: int = 0, total_hypotheses: int = 1) -> List[Dict]:
        """Search literature using LLM-based keyword extraction and strategy with variation for multiple hypotheses"""
        try:
            self.logger.info(f"Searching literature for: {research_goal} (iteration {iteration}, hypothesis variant {hypothesis_index + 1}/{total_hypotheses})")
            
            # Get existing papers for context (extract from existing hypotheses if available)
            existing_papers = []
            for hyp in existing_hypotheses:
                if isinstance(hyp, dict) and hyp.get("literature_sources"):  # Fixed key name
                    existing_papers.extend(hyp["literature_sources"])
                elif isinstance(hyp, dict) and hyp.get("literature_used"):  # Fallback for old key
                    existing_papers.extend(hyp["literature_used"])
            
            self.logger.info(f"Found {len(existing_papers)} existing papers from {len(existing_hypotheses)} previous hypotheses")
            
            # Use the new strategic search approach with variation
            literature = await self.literature_service.search_with_strategy(
                research_goal=research_goal,
                iteration=iteration,
                existing_papers=existing_papers,
                hypothesis_index=hypothesis_index,  # NEW: Pass variation index
                total_hypotheses=total_hypotheses,   # NEW: Pass total count
                limit=15
            )
            
            # Log search results by type
            search_types = {}
            for paper in literature:
                search_type = paper.get("search_type", "unknown")
                search_types[search_type] = search_types.get(search_type, 0) + 1
            
            self.logger.info(f"Search results by type: {search_types}")
            
            return literature
            
        except Exception as e:
            self.logger.error(f"Strategic literature search failed: {str(e)}")
            # Fallback to simple search if strategic approach fails
            return await self._fallback_literature_search(research_goal)
    
    async def _fallback_literature_search(self, research_goal: str) -> List[Dict]:
        """Fallback literature search using simple approach"""
        try:
            # Search both sources concurrently with higher limits
            perplexity_task = self.literature_service.search_academic(research_goal, limit=10)
            pubmed_task = self.literature_service.search_pubmed(research_goal, limit=10)
            
            perplexity_results, pubmed_results = await asyncio.gather(
                perplexity_task, pubmed_task, return_exceptions=True
            )
            
            self.logger.info(f"Perplexity results type: {type(perplexity_results)}")
            self.logger.info(f"PubMed results type: {type(pubmed_results)}")
            
            # Handle potential errors from either source
            combined = []
            
            if isinstance(perplexity_results, list):
                combined.extend(perplexity_results)
                self.logger.info(f"Added {len(perplexity_results)} Perplexity results")
            elif perplexity_results is not None:
                self.logger.warning(f"Perplexity search failed: {perplexity_results}")
            else:
                self.logger.warning("Perplexity search returned None")
            
            if isinstance(pubmed_results, list):
                combined.extend(pubmed_results)
                self.logger.info(f"Added {len(pubmed_results)} PubMed results")
            elif pubmed_results is not None:
                self.logger.warning(f"PubMed search failed: {pubmed_results}")
            else:
                self.logger.warning("PubMed search returned None")
            
            # Ensure we always return a list
            if not combined:
                self.logger.info("No literature found, returning mock data")
                combined = [
                    {
                        "title": f"Mock Paper: Research Approaches to {research_goal}",
                        "abstract": f"This paper discusses various methodological approaches and theoretical frameworks relevant to {research_goal}...",
                        "source": "mock",
                        "relevance_score": 0.8
                    }
                ]
            
            # Return top 15 combined results (increased from 10)
            return combined[:15]
            
        except Exception as e:
            self.logger.error(f"Fallback literature search failed: {str(e)}")
            # Return basic mock data
            return [
                {
                    "title": "Mock Paper: Research Methodologies in Science",
                    "abstract": "This paper discusses various methodological approaches for scientific research investigations...",
                    "source": "mock",
                    "relevance_score": 0.8
                }
            ]
    
    async def _generate_hypothesis(self, goal: str, literature: List[Dict], existing: List[str]) -> str:
        """Generate a novel research hypothesis using Claude"""
        
        # Ensure literature is a list
        if not literature:
            literature = []
        
        # Prepare literature summary - fix the None handling (use more papers)
        literature_summaries = []
        for paper in literature[:8]:  # Increased from 5 to 8
            title = paper.get('title', 'Unknown')
            source = paper.get('source', 'unknown')
            search_type = paper.get('search_type', '')
            
            # Handle abstract/summary more safely
            abstract = paper.get('abstract')
            if not abstract:
                abstract = paper.get('summary')
            if not abstract:
                abstract = 'No abstract available'
            
            # Ensure we have a string to slice
            abstract_text = str(abstract)[:200] + "..." if len(str(abstract)) > 200 else str(abstract)
            
            # Include search context in summary
            context = f" [{source.upper()}" + (f"/{search_type}" if search_type else "") + "]"
            literature_summaries.append(f"- {context} {title}: {abstract_text}")
        
        literature_summary = "\n".join(literature_summaries)
        
        # Prepare existing hypotheses summary (last 3 to avoid duplication)
        existing_summary = ""
        if existing:
            existing_summary = "\n".join([f"- {h}" for h in existing[-3:]])
        
        # Detect domain context for dynamic prompting
        domain_context = await self.literature_service._detect_domain_context(goal)
        
        # Build domain-specific prompt
        expert_role = domain_context.get('expert_role', 'scientific researcher')
        hypothesis_structure = domain_context.get('hypothesis_structure', {
            'elements': ['Approach/Method', 'Target/Problem', 'Mechanism/Theory', 'Rationale', 'Experimental Design'],
            'description': 'research hypothesis'
        })
        
        prompt = f"""
You are a {expert_role}. Based on the research goal and literature, generate a novel {hypothesis_structure['description']}.

Research Goal: {goal}

Recent Literature (with search context):
{literature_summary}

Previous Hypotheses (to avoid duplication):
{existing_summary}

Generate a specific, testable hypothesis including:
1. {hypothesis_structure['elements'][0]} (specific approach or method)
2. {hypothesis_structure['elements'][1]} (specific target or problem)
3. {hypothesis_structure['elements'][2]} (underlying mechanism or theory)
4. {hypothesis_structure['elements'][3]} (why this is novel and promising - 3-4 sentences)
5. {hypothesis_structure['elements'][4]} (specific experimental or validation approach)

Please provide a comprehensive hypothesis that is:
- Novel and not covered in previous hypotheses
- Scientifically grounded based on the literature
- Specific and actionable
- Feasible for experimental testing or validation

Use the search context information to understand how each paper was found and prioritize insights from high-priority searches.

Hypothesis:
"""
        
        try:
            hypothesis = await self.claude_service.generate_hypothesis(prompt, goal)
            
            # Ensure we got a meaningful response
            if not hypothesis or len(hypothesis.strip()) < 100:
                raise Exception("Generated hypothesis too short or empty")
            
            return hypothesis.strip()
            
        except Exception as e:
            self.logger.error(f"Claude hypothesis generation failed: {str(e)}")
            # Return a fallback hypothesis
            return f"""
Hypothesis: Novel approach to {goal}

Approach: Systematic investigation using established scientific methodologies
Target: Core challenges related to {goal}
Mechanism: Evidence-based theoretical framework from current literature
Rationale: This represents a novel application based on emerging research trends and addresses gaps in current understanding
Experimental Design: Structured investigation with appropriate controls and validation methods

Note: This is a fallback hypothesis generated due to API limitations.
""" 
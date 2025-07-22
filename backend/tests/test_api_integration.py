import pytest
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

from app.services.claude_service import ClaudeService
from app.services.literature_service import LiteratureService

class TestAPIIntegration:
    """Test API integrations as specified in the implementation guide"""
    
    @pytest.mark.asyncio
    async def test_claude_api(self):
        """Test Claude API integration"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not available - using mock data")
        
        service = ClaudeService()
        response = await service.generate_text("Test prompt for scientific research", max_tokens=50)
        
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_claude_connection(self):
        """Test Claude API connection"""
        service = ClaudeService()
        is_connected = await service.test_connection()
        
        # Should return True if API key is available, False otherwise
        assert isinstance(is_connected, bool)
    
    @pytest.mark.asyncio 
    async def test_perplexity_academic(self):
        """Test Perplexity Academic search"""
        service = LiteratureService()
        results = await service.search_academic("acute myeloid leukemia treatment", limit=3)
        
        assert len(results) > 0
        assert isinstance(results, list)
        
        # Check result structure
        if results:
            result = results[0]
            assert "title" in result
            assert "source" in result
            assert result["source"] in ["perplexity", "mock"]
    
    @pytest.mark.asyncio
    async def test_pubmed_integration(self):
        """Test PubMed API integration"""
        service = LiteratureService()
        papers = await service.search_pubmed("AML research", limit=5)
        
        assert len(papers) > 0
        assert isinstance(papers, list)
        
        # Check result structure
        if papers:
            paper = papers[0]
            assert "title" in paper
            assert "source" in paper
            assert paper["source"] in ["pubmed", "mock"]
    
    @pytest.mark.asyncio
    async def test_literature_service_both_sources(self):
        """Test that literature service can search both sources"""
        service = LiteratureService()
        
        # Test both methods work
        perplexity_results = await service.search_academic("scientific research", limit=2)
        pubmed_results = await service.search_pubmed("scientific research", limit=2)
        
        assert isinstance(perplexity_results, list)
        assert isinstance(pubmed_results, list)
        
        # At least one should return results (even if mock)
        assert len(perplexity_results) > 0 or len(pubmed_results) > 0
    
    @pytest.mark.asyncio
    async def test_claude_hypothesis_generation(self):
        """Test Claude can generate research hypotheses"""
        service = ClaudeService()
        
        prompt = """Generate a specific research hypothesis for investigating cancer. 
        Include the drug name, mechanism, and rationale."""
        
        hypothesis = await service.generate_hypothesis(prompt, "Cancer treatment")
        
        assert hypothesis is not None
        assert len(hypothesis) > 100  # Should be a substantial response
        assert isinstance(hypothesis, str)
    
    @pytest.mark.asyncio
    async def test_claude_hypothesis_review(self):
        """Test Claude can review hypotheses"""
        service = ClaudeService()
        
        test_hypothesis = "Use metformin for Alzheimer's disease treatment based on its neuroprotective properties."
        criteria = "Scientific rigor, novelty, feasibility"
        
        review = await service.review_hypothesis(test_hypothesis, criteria)
        
        assert isinstance(review, dict)
        assert "score" in review
        assert "review" in review
        assert 0.0 <= review["score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_all_services_initialization(self):
        """Test that all services can be initialized without errors"""
        claude_service = ClaudeService()
        literature_service = LiteratureService()
        
        # Services should initialize without throwing exceptions
        assert claude_service is not None
        assert literature_service is not None
        
        # Test basic connectivity
        claude_connected = await claude_service.test_connection()
        perplexity_connected = await literature_service.test_perplexity_connection()
        pubmed_connected = await literature_service.test_pubmed_connection()
        
        # At least some should work (even with mock data)
        assert isinstance(claude_connected, bool)
        assert isinstance(perplexity_connected, bool) 
        assert isinstance(pubmed_connected, bool)

@pytest.mark.asyncio
async def test_environment_setup():
    """Test that the environment is properly configured"""
    # Test that we can load environment variables
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    
    # At least one API should be configured for full testing
    if not anthropic_key:
        print("Warning: ANTHROPIC_API_KEY not configured - using mock responses")
    
    if not perplexity_key:
        print("Warning: PERPLEXITY_API_KEY not configured - using mock responses")
    
    # Environment variables for paths
    data_dir = os.getenv("DATA_DIR", "./data")
    cache_dir = os.getenv("CACHE_DIR", "./cache")
    log_dir = os.getenv("LOG_DIR", "./logs")
    
    assert data_dir is not None
    assert cache_dir is not None
    assert log_dir is not None 
# AI Co-Scientist

A domain-agnostic multi-agent AI system for scientific research that demonstrates test-time compute scaling and collaborative reasoning across diverse scientific disciplines.

## Overview

This system implements an advanced multi-agent framework with three specialized AI agents that adapt to any scientific domain:

- **Generation Agent**: Creates novel research hypotheses using sophisticated literature search and domain-aware AI reasoning
- **Reflection Agent**: Reviews and critiques hypotheses to improve quality and scientific rigor across all domains
- **Ranking Agent**: Compares and ranks multiple hypotheses based on scientific merit and domain-specific criteria

### Key Features

- **Universal Domain Support**: Automatically detects and adapts to any scientific field including medicine, physics, chemistry, computer science, biology, climate science, environmental science, psychology, engineering, and mathematics
- **Configurable Research Parameters**: Generate 1-5 hypotheses per iteration across 1-10 iterations for scalable research exploration
- **Unique Literature Per Hypothesis**: Each hypothesis receives distinct literature through specialized search strategies (foundational, recent advances, interdisciplinary, methodological, critical perspectives)
- **Multi-Source Literature Search**: Integrates Perplexity Academic, PubMed, and Google Scholar with LLM-optimized query generation
- **Real-Time Research Monitoring**: Live WebSocket updates showing agent progress and hypothesis development

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│     Frontend        │    │      Backend        │
│   (React + JS)      │◄──►│   (FastAPI + Python)│
│                     │    │                     │
│  • Research UI      │    │  • Agent System     │
│  • Domain Detection │    │  • Literature Engine│
│  • Real-time Updates│    │  • API Integration  │
│  • Parameter Control│    │  • Data Storage     │
└─────────────────────┘    └─────────────────────┘
                                      │
                           ┌─────────────────────┐
                           │   External APIs     │
                           │                     │
                           │ • Claude Sonnet-4   │
                           │ • Perplexity Academic│
                           │ • PubMed Database   │
                           │ • Google Scholar API│
                           │ • Serper API        │
                           └─────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- API Keys (see setup below)

### 1. Environment Setup

Create a `.env` file in the project root:

```env
# AI Model APIs
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here

# Literature Search APIs
SERPER_API_KEY=your-serper-api-key-here
PUBMED_EMAIL=your-email@domain.com

# Development Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Agent System Settings
MAX_ITERATIONS=10
GENERATION_TIMEOUT=300
REFLECTION_TIMEOUT=180
RANKING_TIMEOUT=120

# Data Storage
DATA_DIR=./data
CACHE_DIR=./cache
LOG_DIR=./logs
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python run.py
```

The backend will start at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start at `http://localhost:3000`

## System Capabilities

### Domain-Adaptive Research

The system automatically detects research domains and adapts its entire workflow:

#### Supported Domains
- **Medicine**: Clinical research, drug development, medical hypotheses
- **Physics**: Theoretical physics, experimental design, computational physics
- **Chemistry**: Chemical synthesis, reaction mechanisms, materials science
- **Computer Science**: Algorithm development, system design, computational methods
- **Biology**: Molecular biology, genetics, systems biology, ecology
- **Climate Science**: Climate modeling, atmospheric research, environmental impact
- **Environmental Science**: Sustainability research, ecosystem studies, pollution analysis
- **Psychology**: Behavioral research, cognitive studies, experimental psychology
- **Engineering**: System design, optimization, technological solutions
- **Mathematics**: Theoretical mathematics, applied mathematics, statistical methods

#### Adaptive Features
- **Expert Role Assignment**: AI agents assume appropriate domain expertise
- **Domain-Specific Terminology**: Uses field-appropriate language and concepts
- **Specialized Literature Sources**: Prioritizes relevant academic databases
- **Hypothesis Structure**: Adapts hypothesis format to domain conventions

### Advanced Literature Search

#### Multi-Source Integration
- **Perplexity Academic**: Recent papers, preprints, and cutting-edge research
- **PubMed**: Comprehensive biomedical and life science literature
- **Google Scholar**: Broad academic coverage across all disciplines

#### LLM-Powered Query Optimization
- **Two-Stage Process**: Analysis stage followed by strategy optimization
- **Domain-Aware Queries**: Search terms adapted to specific research fields
- **Iteration-Aware Strategy**: Search focus evolves across iterations for broader exploration
- **Multiple Query Types**: Primary (specific), secondary (broader), discovery (novel connections)

#### Unique Literature Per Hypothesis
Each hypothesis receives distinct supporting literature through specialized search strategies:
1. **Foundational Literature**: Seminal papers and established theories
2. **Recent Advances**: Cutting-edge research and novel methodologies
3. **Interdisciplinary Connections**: Cross-domain research and hybrid approaches
4. **Methodological Innovations**: New techniques and experimental methods
5. **Critical Perspectives**: Challenges, limitations, and alternative viewpoints

### Research Configuration

#### Flexible Parameters
- **Iterations**: Configure 1-10 iterations for varying research depth
- **Hypotheses Per Iteration**: Generate 1-5 hypotheses per iteration for different coverage levels
- **Literature Diversity**: Each hypothesis backed by unique, strategically selected literature

#### Quality Assessment
Each hypothesis is evaluated across multiple dimensions:
- **Scientific Rigor** (25% weight): Methodological soundness and theoretical foundation
- **Novelty** (20% weight): Innovation and originality of approach
- **Feasibility** (25% weight): Practical implementability and resource requirements
- **Impact Potential** (20% weight): Significance and broader implications
- **Specificity** (10% weight): Clarity and actionability of research direction

## Testing the System

### 1. API Integration Test

Visit the API Testing tab to verify:
- Claude Sonnet-4 connection
- Perplexity Academic search functionality
- PubMed database access
- Google Scholar integration
- Domain detection accuracy

### 2. Domain-Specific Research Sessions

Example research questions across domains:

**Medicine**: "What are novel approaches for treating neurodegenerative diseases?"
**Physics**: "How can we improve quantum coherence in solid-state systems?"
**Climate Science**: "What are the most effective carbon capture technologies?"
**Computer Science**: "How can machine learning improve protein structure prediction?"
**Chemistry**: "What catalysts show promise for sustainable chemical synthesis?"

### 3. Parameter Configuration

1. Set research parameters:
   - Max Iterations: 1-10 (higher values for deeper exploration)
   - Hypotheses per Iteration: 1-5 (higher values for broader coverage)

2. Monitor real-time progress:
   - Agent status updates
   - Literature search progress
   - Hypothesis generation and review
   - Quality scoring and ranking

### 4. Backend API Testing

```bash
cd backend

# Run integration tests
pytest tests/test_api_integration.py -v

# Test individual agents
curl -X POST "http://localhost:8000/api/agents/generation/test"
curl -X POST "http://localhost:8000/api/agents/reflection/test"  
curl -X POST "http://localhost:8000/api/agents/ranking/test"

# Test domain detection
curl -X POST "http://localhost:8000/api/research/detect-domain" \
  -H "Content-Type: application/json" \
  -d '{"research_question": "How can we improve solar cell efficiency?"}'
```

## Research Workflow

### Multi-Agent Process

1. **Domain Detection**: System identifies the research field and configures appropriate parameters
2. **Generation Phase**: 
   - Each hypothesis receives unique literature search with domain-specific queries
   - LLM generates hypotheses using specialized prompts for the detected domain
   - Multiple hypotheses created per iteration based on configuration
3. **Reflection Phase**: 
   - Domain-aware quality assessment using field-specific criteria
   - Scientific rigor evaluated according to domain standards
   - Individual scoring for each hypothesis
4. **Ranking Phase**: 
   - Comparative analysis using domain-appropriate metrics
   - Prioritization based on scientific merit and potential impact
   - Final ranking across all generated hypotheses

### Iteration Scaling

- **Early Iterations**: Focus on direct relationships and established mechanisms
- **Later Iterations**: Explore broader connections and novel mechanisms
- **Progressive Improvement**: Each iteration builds on previous findings
- **Literature Expansion**: Search strategies adapt to avoid redundancy

## Development

### Project Structure

```
ai-co-scientist/
├── .env                    # Environment configuration
├── README.md              # This documentation
├── backend/               # Python FastAPI backend
│   ├── app/
│   │   ├── agents/        # AI agent implementations
│   │   ├── services/      # External API integrations
│   │   ├── models/        # Data models and schemas
│   │   ├── api/           # REST and WebSocket APIs
│   │   └── utils/         # Utilities and helpers
│   ├── tests/             # Backend tests
│   ├── requirements.txt   # Python dependencies
│   └── run.py             # Server entry point
├── frontend/              # React JavaScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── services/      # API clients
│   ├── package.json       # Node dependencies
│   └── public/            # Static assets
└── data/                  # Generated data and logs
    ├── sessions/          # Research session data
    ├── hypotheses/        # Generated hypotheses
    └── cache/             # Literature search cache
```

### Key Development Commands

```bash
# Backend Development
cd backend
python run.py                    # Start development server
pytest tests/ -v                 # Run all tests
python -m pytest tests/test_api_integration.py -v  # Run integration tests

# Frontend Development  
cd frontend
npm start                        # Start development server
npm test                         # Run tests
npm run build                    # Build for production

# Full System Test
# Terminal 1: Start backend
cd backend && python run.py

# Terminal 2: Start frontend  
cd frontend && npm start

# Terminal 3: Run comprehensive tests
cd backend && pytest tests/test_api_integration.py -v
```

## Performance Characteristics

### Expected Response Times
- **Domain Detection**: < 2 seconds
- **Literature Search**: 10-30 seconds (depending on sources and complexity)
- **Hypothesis Generation**: 30-90 seconds per hypothesis
- **Hypothesis Review**: 20-40 seconds per hypothesis
- **Complete Research Session**: 2-15 minutes (varies by configuration)

### Scaling Considerations
- **Iteration Scaling**: Each iteration demonstrates measurable quality improvement
- **Hypothesis Diversity**: Multiple hypotheses per iteration provide comprehensive coverage
- **Literature Caching**: Reduces redundant API calls and improves performance
- **Parallel Processing**: Multiple hypotheses processed concurrently within iterations
- **Real-Time Updates**: WebSocket connections provide responsive user experience

## Troubleshooting

### Common Issues

**Backend Connection Issues**
- Verify Python 3.8+ is installed
- Check that port 8000 is available
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**API Authentication Failures**
- Verify all API keys are correctly set in `.env` file
- Check API key validity and rate limits
- Ensure internet connectivity for external API calls

**Frontend Connection Issues**
- Confirm backend is running on port 8000
- Check browser console for JavaScript errors
- Verify WebSocket connection establishment

**Domain Detection Issues**
- Verify Claude API key is valid
- Check research question clarity and specificity
- Review system logs for domain detection details

### Fallback Mechanisms

The system includes robust fallback mechanisms:

**API Failures**
- **Claude API**: Falls back to structured templates when unavailable
- **Perplexity API**: Uses mock academic data for testing
- **PubMed API**: Provides sample research papers
- **Google Scholar API**: Returns mock citation data

**Domain Detection**
- **Unknown Domains**: Default to general scientific research approach
- **Ambiguous Questions**: Use broad domain-agnostic strategies
- **API Unavailable**: Apply general research methodology templates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Implement changes with appropriate tests
4. Commit changes (`git commit -m 'Add feature enhancement'`)
5. Push to branch (`git push origin feature/enhancement`)
6. Create a Pull Request

### Development Guidelines

- Maintain domain-agnostic design principles
- Add appropriate test coverage for new features
- Follow existing code structure and patterns
- Update documentation for new capabilities
- Test across multiple scientific domains

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Anthropic for Claude Sonnet-4 API access
- Perplexity AI for Academic Search API
- NIH/NLM for PubMed database access
- Serper for Google Scholar API integration
- FastAPI and React development communities 